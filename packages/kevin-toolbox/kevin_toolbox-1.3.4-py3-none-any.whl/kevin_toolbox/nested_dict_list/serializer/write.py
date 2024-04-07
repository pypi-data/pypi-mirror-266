import os
import time
import warnings
import kevin_toolbox
from kevin_toolbox.data_flow.file import json_
from kevin_toolbox.patches import for_os
import kevin_toolbox.nested_dict_list as ndl
from kevin_toolbox.nested_dict_list.traverse import Traversal_Mode
from .enum_variable import Strictness_Level
from .saved_node_name_builder import Saved_Node_Name_Builder


def write(var, output_dir, settings=None, traversal_mode=Traversal_Mode.BFS, b_pack_into_tar=True,
          strictness_level=Strictness_Level.COMPATIBLE, saved_node_name_format='{count}_{hash_name}',
          b_keep_identical_relations=False, **kwargs):
    """
        将输入的嵌套字典列表 var 的结构和节点值保存到文件中
            遍历 var，匹配并使用 settings 中设置的保存方式来对各部分结构/节点进行序列化
            将会生成一个文件夹或者 .tar 文件，其中包含：
                - var.json：     用于保存结构、简单节点值、复杂节点值/结构的序列化方式
                - nodes/：       该目录中包含一系列 <name>.<suffix> 文件或者 <name> 文件夹，其中包含复杂节点值/结构的序列化结果
                - record.json：   其中记录了：
                                        {
                                            "processed": ... # 对哪些节点/部分进行了处理
                                            "raw_structure": ... # 原始结构
                                            "timestamp": ... # 保存时间
                                            "kt_version": ... # 使用哪个版本下的 kevin_toolbox
                                        }

        参数：
            var:                    <nested dict list>
            settings:               <list of dict> 指定对于不同节点or部分的处理模式
                                        其结构为：
                                            [{"match_cond": <匹配模式>, "backend": <序列化方式>, "traversal_mode": <遍历方式>}, ...]
                                        <匹配模式>支持以下4种：
                                            - "<level>..."  匹配指定层的节点，比如"<level>0"表示根节点，"<level>-1"表示所有叶节点
                                            - "<node>name"  匹配指定name的节点
                                            - callable      一个形如 def(parent_type, idx, value): ... 的函数，各参数具体意义
                                                                见 traverse() 中的 match_cond 参数。函数返回 True 时视为匹配成功。
                                            - "<eval>..."   将使用 eval() 将该字符串解释为上面形式的函数来进行匹配。
                                        <序列化方式>默认支持以下几种及其组合：
                                            - ":skip:simple"    若对象为 int、float、str、None 或者 tuple of 前者的组合，则不做处理直接保留在结构中
                                            - ":skip:all"       不做处理直接保留在结构中
                                            - ":numpy:bin"      若对象为 np.array，则以 bin file 的形式进行序列化
                                            - ":numpy:npy"      若对象为 np.array，则以 .npy 的形式进行序列化
                                            - ":torch:tensor"   若对象为 torch.tensor，则调用 torch 中的 load 和 save 进行序列化
                                            - ":torch:all"      调用 torch 中的 load() 和 save() 进行序列化
                                            - ":json"           若对象可以被 json 格式保存，则将其按照 json 格式进行序列化
                                            - ":pickle"         调用 pickle 中的 load() 和 save() 进行序列化
                                            - ":ndl"            调用本模块 nested_dict_list 中的 read() 和 write() 进行序列化
                                                                    利用该方式可以实现递归的序列化
                                        比如组合 (":skip:simple", ":numpy:bin", ":torch:tensor", ":pickle") 则表示根据变量的类型，依次尝试这几种方式
                                            直至成功。其含义为：
                                                - 如果是可以直接写入到 json 中的 int、float、str、None以及简单的 tuple 等则选用 ":skip:simple"
                                                - 如果是 np.array 则选用 ":numpy:bin"
                                                - 如果是 tensor 则选用 ":torch:tensor"
                                                - 其他无法处理的类型则选用 ":pickle"
                                        <序列化方式>允许进行自定义扩增，若要添加新的<序列化方式>，可以实现一个带有：
                                                - write(name, var):         序列化
                                                - read(name):               反序列化
                                                - writable(var):            是否可以写
                                                - readable(name):           是否可以读
                                            等方法的序列化 backend 类，然后将其实例注册到 SERIALIZER_BACKEND 中，具体可以参考
                                            backends._torch_tensor.py 中的实现方式。
                                        <遍历方式>支持以下3种:
                                            - "dfs_pre_order"         深度优先、先序遍历
                                            - "dfs_post_order"        深度优先、后序遍历
                                            - "bfs"                   宽度优先
                                            省略时默认使用参数 traversal_mode 中的设置，更多参考 traverse() 中的介绍。
                                        默认的处理模式是：
                                            [{"match_cond": "<level>-1", "backend": (":skip:simple", ":numpy:npy", ":torch:tensor", ":pickle")}]
            traversal_mode:         <str> 遍历方式
                                        默认使用 "bfs"
            output_dir:             <path> 输出文件夹
            b_pack_into_tar:        <boolean> 是否将输出打包成 tar 文件
                                        默认是 True，此时结果将保存到 /<output_dir>.tar 下。
            strictness_level:       <str/Strictness_Level> 对写入过程中正确性与完整性的要求的严格程度
                                        有以下可选项：
                                            - "high" / Strictness_Level.COMPLETE        所有节点均有一个或者多个匹配上的 backend，
                                                                                            且第一个匹配上的 backend 就成功写入。
                                            - "normal" / Strictness_Level.COMPATIBLE    所有节点均有一个或者多个匹配上的 backend，
                                                                                            但是首先匹配到的 backend 写入出错，
                                                                                            使用其后再次匹配到的其他 backend 能够成功写入
                                            - "low" / Strictness_Level.IGNORE_FAILURE   匹配不完整，或者某些节点尝试过所有匹配到
                                                                                            的 backend 之后仍然无法写入
                                        默认是 "normal"
            saved_node_name_format: <str> nodes/目录下节点文件/文件夹的命名方式。
                                        基本结构为：  '{<part_0>}...{<part_1>}...'
                                        其中 {} 内将根据 part 指定的类型进行自动填充。目前支持以下几种选项：
                                            - "raw_name"        该节点对应位置的 name。
                                            - "id"              该节点在当前内存中的 id。
                                            - "hash_name"       该节点位置 name 的 hash 值。
                                            - "count"           累加计算，表示是保存的第几个节点。
                                        ！！注意：
                                            "raw_name" 该选项在 v1.3.3 前被使用，但是由于其可能含有 : 和 / 等特殊符号，当以其作为文件夹名时，
                                                可能会引发错误。因此对于 windows 用户，禁止使用该选项，对于 mac 和 linux 用户，同样也不建议使用该选项。
                                            "id" 虽然具有唯一性，但是其值对于每次运行是随机的。
                                            "hash_name" 有极低的可能会发生 hash 碰撞。
                                        综合而言：
                                            建议使用 "hash_name" 和 "count" 的组合。
                                        默认值为：
                                            '{count}_{hash_name}'
            b_keep_identical_relations: <boolean> 是否保留不同节点之间的 id 相等关系。
                                        具体而言，就是使用 value_parser.replace_identical_with_reference() 函数将具有相同 id 的多个节点，
                                            替换为单个节点和其多个引用的形式。
                                        对于 ndl 中存在大量具有相同 id 的重复节点的情况，使用该操作可以额外达到压缩的效果。
                                        默认为 False
    """
    from kevin_toolbox.nested_dict_list.serializer.variable import SERIALIZER_BACKEND

    # 检查参数
    traversal_mode = Traversal_Mode(traversal_mode)
    strictness_level = Strictness_Level(strictness_level)
    os.makedirs(output_dir, exist_ok=True)
    var = ndl.copy_(var=var, b_deepcopy=False)
    if b_keep_identical_relations:
        from kevin_toolbox.nested_dict_list import value_parser
        var = value_parser.replace_identical_with_reference(var=var, flag="same", b_reverse=False)
    if settings is None:
        settings = [{"match_cond": "<level>-1", "backend": (":skip:simple", ":numpy:npy", ":torch:tensor", ":pickle")}]
    snn_builder = Saved_Node_Name_Builder(format_=saved_node_name_format)

    # 构建 processed_s
    #     为了避免重复处理节点/结构，首先构建与 var 具有相似结构的 processed_s 来记录处理处理进度。
    #     对于 processed_s，其节点值为 True 时表示该节点已经被处理，当节点值为 False 或者 list/dict 类型时表示该节点或者节点下面的结构中仍然
    #       存在未处理的部分。
    #     对于中间节点，只有其下所有叶节点都未处理时才会被匹配。
    processed_s = ndl.copy_(var=var, b_deepcopy=False, b_keep_internal_references=False)
    for n, _ in ndl.get_nodes(var=var, level=-1, b_strict=True):
        ndl.set_value(var=processed_s, name=n, value=False, b_force=False)
    # processed_s_bak 用于记录 var 的原始结构
    processed_s_bak = ndl.copy_(var=processed_s, b_deepcopy=True)
    if "_hook_for_debug" in kwargs:
        kwargs["_hook_for_debug"]["processed"] = [["raw", ndl.copy_(var=processed_s, b_deepcopy=True)], ]

    # 处理 var
    backend_s = dict()
    for setting in settings:
        # match_cond
        if isinstance(setting["match_cond"], str) and setting["match_cond"].startswith("<eval>"):
            setting["match_cond"] = eval(setting["match_cond"][6:])
        assert callable(setting["match_cond"]) or isinstance(setting["match_cond"], str)
        # backend
        backend_name_ls = setting["backend"] if isinstance(setting["backend"], (list, tuple)) else [setting["backend"]]
        for i in backend_name_ls:
            if i not in backend_s:
                backend_s[i] = SERIALIZER_BACKEND.get(name=i)(folder=os.path.join(output_dir, "nodes"))
        #
        t_mode = Traversal_Mode(setting.get("traversal_mode", traversal_mode))
        # _process and  paras
        if callable(setting["match_cond"]):
            if t_mode in (Traversal_Mode.DFS_PRE_ORDER, Traversal_Mode.BFS):
                _process = _process_from_top_to_down
            else:
                _process = _process_from_down_to_top
            paras = dict(var=var, match_cond=setting["match_cond"], traversal_mode=t_mode)
        elif setting["match_cond"].startswith("<level>"):
            _process = _process_for_level
            paras = dict(var=var, processed_s_bak=processed_s_bak, level=int(setting["match_cond"][7:]))
        elif setting["match_cond"].startswith("<node>"):
            _process = _process_for_name
            paras = dict(var=var, name=setting["match_cond"][6:])
        else:
            raise ValueError(f'invalid match_cond: {setting["match_cond"]}')
        # 执行
        for i in backend_name_ls:
            # print(processed_s)
            # print(f'backend: {i}')
            _process(backend=backend_s[i], strictness_level=strictness_level, processed_s=processed_s,
                     snn_builder=snn_builder, **paras)
            if "_hook_for_debug" in kwargs:
                kwargs["_hook_for_debug"]["processed"].append([i, ndl.copy_(var=processed_s, b_deepcopy=True)])

    # print(processed_s)
    # print(var)

    # 完整性检查
    failed_nodes = [n for n, v in ndl.get_nodes(var=processed_s, level=-1) if not v]
    if strictness_level is Strictness_Level.IGNORE_FAILURE:
        for n in failed_nodes:
            ndl.set_value(var=var, name=n, value=None, b_force=False)
    else:
        for n in failed_nodes:
            warnings.warn(
                message=f'node {n} failed to write',
                category=UserWarning
            )
        assert len(failed_nodes) == 0, \
            f'please check settings to make sure all nodes have been covered and can be deal with backend'

    # 保存 var 的结构
    json_.write(content=var, file_path=os.path.join(output_dir, "var.json"), b_use_suggested_converter=True)
    # 保存处理结果（非必要）
    json_.write(content=dict(processed=processed_s, raw_structure=processed_s_bak, timestamp=time.time(),
                             kt_version=kevin_toolbox.__version__,
                             b_keep_identical_relations=b_keep_identical_relations),
                file_path=os.path.join(output_dir, "record.json"), b_use_suggested_converter=True)

    # 打包成 .tar 文件
    if b_pack_into_tar:
        for_os.pack(source=output_dir)
        for_os.remove(path=output_dir, ignore_errors=True)


def _judge_processed_or_not(processed_s, name):
    """
        如 name 所指向的节点已经被处理，或者节点下的部分含有已经处理的子节点，则返回 True
    """
    b_processed = ndl.get_value(var=processed_s, name=name, b_pop=False, default=True)
    if not isinstance(b_processed, bool):
        # 需要查清楚下面子节点是否存在未处理的部分
        for n, v in ndl.get_nodes(var=b_processed, level=-1, b_strict=True):
            if v:
                b_processed = True
                break
        else:
            b_processed = False
    return b_processed


def _process_for_level(var, processed_s, processed_s_bak, level, backend, strictness_level, snn_builder):
    for name, _ in ndl.get_nodes(var=processed_s_bak, level=level, b_strict=True):
        _process_for_name(var=var, processed_s=processed_s, name=name, backend=backend,
                          strictness_level=strictness_level, snn_builder=snn_builder)


def _process_for_name(var, processed_s, name, backend, strictness_level, snn_builder):
    if _judge_processed_or_not(processed_s=processed_s, name=name) is True:
        # has been processed
        return
    value = ndl.get_value(var=var, name=name, b_pop=False)
    if not backend.writable(var=value):
        # cannot be written by backend
        return

    # write by backend
    snn_name = snn_builder(name=name, value=value)
    try:
        res = backend.write(name=snn_name, var=value)
    except:
        assert strictness_level in (Strictness_Level.IGNORE_FAILURE, Strictness_Level.COMPATIBLE), \
            f'An error occurred when node {name} was saved using the first matched backend {backend}'
        return
    ndl.set_value(var=processed_s, name=name, value=True, b_force=False)
    ndl.set_value(var=var, name=name, value=res, b_force=False)


def _process_from_top_to_down(var, processed_s, match_cond, backend, traversal_mode, strictness_level, snn_builder):
    def match_cond_(parent_type, idx, value):
        nonlocal match_cond, processed_s

        b_processed = _judge_processed_or_not(processed_s=processed_s, name=idx)
        if b_processed is True or not backend.writable(var=value):
            # has been processed or cannot be written by backend
            return False

        return match_cond(parent_type, idx, value)

    def converter(idx, value):
        nonlocal processed_s, backend, strictness_level

        # write by backend
        snn_name = snn_builder(name=idx, value=value)
        try:
            res = backend.write(name=snn_name, var=value)
        except:
            assert strictness_level in (Strictness_Level.IGNORE_FAILURE, Strictness_Level.COMPATIBLE), \
                f'An error occurred when node {name} was saved using the first matched backend {backend}'
            return value
        ndl.set_value(var=processed_s, name=idx, value=True, b_force=True)
        return res

    ndl.traverse(var=var, match_cond=match_cond_, action_mode="replace", converter=converter,
                 b_use_name_as_idx=True, traversal_mode=traversal_mode, b_traverse_matched_element=False)


def _process_from_down_to_top(var, processed_s, match_cond, backend, traversal_mode, strictness_level, snn_builder):
    processed_s_raw, processed_s = processed_s, ndl.copy_(var=processed_s, b_deepcopy=True)

    def match_cond_(parent_type, idx, value):
        nonlocal match_cond, processed_s

        b_processed = _judge_processed_or_not(processed_s=processed_s, name=idx)
        ndl.set_value(var=processed_s, name=idx, value=b_processed, b_force=False)
        if b_processed is True or not backend.writable(var=value):
            # has been processed or cannot be written by backend
            return False

        return match_cond(parent_type, idx, value)

    def converter(idx, value):
        nonlocal processed_s, backend, processed_s_raw, strictness_level

        # write by backend
        snn_name = snn_builder(name=idx, value=value)
        try:
            res = backend.write(name=snn_name, var=value)
        except:
            assert strictness_level in (Strictness_Level.IGNORE_FAILURE, Strictness_Level.COMPATIBLE), \
                f'An error occurred when node {name} was saved using the first matched backend {backend}'
            return value
        ndl.set_value(var=processed_s, name=idx, value=True, b_force=True)
        ndl.set_value(var=processed_s_raw, name=idx, value=True, b_force=True)
        return res

    ndl.traverse(var=var, match_cond=match_cond_, action_mode="replace", converter=converter,
                 b_use_name_as_idx=True, traversal_mode=traversal_mode)


if __name__ == '__main__':
    import torch
    import numpy as np
    from kevin_toolbox.nested_dict_list import name_handler

    var_ = {
        "a": np.random.rand(2, 5),
        "b": [torch.randn(5), torch.randn(3)],
        (1, 2, 3): (1, 2, 3),
        "model": dict(name="m", paras=dict(paras=dict(layer_nums=3, input_shape=np.random.rand(2, 5))))
    }
    # var_ = None

    _hook_for_debug = dict()
    settings_ = [
        {"match_cond": lambda _, idx, value: "paras" == name_handler.parse_name(name=idx)[2][-1],
         "backend": (":pickle",),
         "traversal_mode": "dfs_post_order"},
        {"match_cond": "<level>-1",
         "backend": (":numpy:bin", ":torch:tensor")},
        {"match_cond": lambda _, __, value: not isinstance(value, (list, dict)),
         "backend": (":skip:simple",)},
    ]
    write(var=var_, output_dir=os.path.join(os.path.dirname(__file__), "temp"), traversal_mode="bfs",
          b_pack_into_tar=True, settings=settings_, _hook_for_debug=_hook_for_debug)

    for bk_name, p in _hook_for_debug["processed"]:
        print(f'backend: {bk_name}')
        print(p)
