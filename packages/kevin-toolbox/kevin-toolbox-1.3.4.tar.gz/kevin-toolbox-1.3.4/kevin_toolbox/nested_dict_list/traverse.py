from enum import Enum
from kevin_toolbox.nested_dict_list.name_handler import escape_node


class Action_Mode(Enum):
    REMOVE = "remove"
    REPLACE = "replace"
    SKIP = "skip"


class Traversal_Mode(Enum):
    DFS_PRE_ORDER = "dfs_pre_order"
    DFS_POST_ORDER = "dfs_post_order"
    BFS = "bfs"


def traverse(var, match_cond, action_mode="remove", converter=None,
             b_use_name_as_idx=False, traversal_mode="dfs_pre_order", b_traverse_matched_element=False):
    """
        遍历 var 找到符合 match_cond 的元素，将其按照 action_mode 指定的操作进行处理

        参数：
            var:                待处理数据
                                    当 var 不是 dict 或者 list 时，将直接返回 var 而不做处理
            match_cond:         <func> 元素的匹配条件
                                    函数类型为 def(parent_type, idx, value): ...
                                    其中：
                                        parent_type     该元素源自哪种结构体，有两个可能传入的值： list，dict
                                        idx             该元素在结构体中的位置
                                                            当 b_use_name_as_idx=False 时，
                                                                对于列表是 index，对于字典是 key
                                                            当为 True 时，传入的是元素在整体结构中的 name 位置，name的格式和含义参考
                                                                name_handler.parse_name() 中的介绍
                                        value           元素的值
            action_mode:        <str> 如何对匹配上的元素进行处理
                                    目前支持：
                                        "remove"        将该元素移除
                                        "replace"       将该元素替换为 converter() 处理后的结果
                                        "skip":         不进行任何操作
            converter:          <func> 参见 action_mode 中的 "replace" 模式
                                    函数类型为 def(idx, value): ...
                                    其中 idx 和 value 的含义参见参数 match_cond 介绍
            traversal_mode:     <str> 遍历的模式、顺序
                                    目前支持：
                                        "dfs_pre_order"         深度优先、先序遍历
                                        "dfs_post_order"        深度优先、后序遍历
                                        "bfs"                   宽度优先
                                    默认为 "dfs_pre_order"
            b_use_name_as_idx:  <boolean> 对于 match_cond/converter 中的 idx 参数，是传入整体的 name 还是父节点的 index 或 key。
                                    默认为 False
            b_traverse_matched_element  <boolean> 对于匹配上的元素，经过处理后，是否继续遍历该元素的内容
                                    默认为 False
    """
    assert callable(match_cond)
    action_mode = Action_Mode(action_mode)
    if action_mode is Action_Mode.REPLACE:
        assert callable(converter)
    traversal_mode = Traversal_Mode(traversal_mode)

    if traversal_mode is Traversal_Mode.BFS:
        return _bfs(var, match_cond, action_mode, converter, b_use_name_as_idx, b_traverse_matched_element)
    else:
        return _dfs(var, match_cond, action_mode, converter, b_use_name_as_idx, traversal_mode,
                    b_traverse_matched_element, "")


def _bfs(var, match_cond, action_mode, converter, b_use_name_as_idx, b_traverse_matched_element):
    temp = [("", var)]

    while len(temp):
        pre_name, i = temp.pop(0)
        if isinstance(i, (list, dict)):
            keys = list(range(len(i)) if isinstance(i, list) else i.keys())
            keys.reverse()  # 反过来便于 列表 弹出元素
            idx_ls = _gen_idx(i, keys, b_use_name_as_idx, pre_name)

            # 匹配&处理
            for k, idx in zip(keys, idx_ls):
                b_matched, b_popped = _deal(i, k, idx, match_cond, converter, action_mode)
                if b_popped or (b_matched and not b_traverse_matched_element):
                    continue
                # 添加到队尾
                temp.append((idx, i[k]))

    return var


def _dfs(var, match_cond, action_mode, converter,
         b_use_name_as_idx, traversal_mode, b_traverse_matched_element, pre_name):
    if isinstance(var, (list, dict)):
        keys = list(range(len(var)) if isinstance(var, list) else var.keys())
        keys.reverse()  # 反过来便于 列表 弹出元素
        idx_ls = _gen_idx(var, keys, b_use_name_as_idx, pre_name)

        #
        if traversal_mode is Traversal_Mode.DFS_PRE_ORDER:
            # 先序
            # 匹配&处理
            deal_res_ls = []
            for k, idx in zip(keys, idx_ls):
                deal_res_ls.append(_deal(var, k, idx, match_cond, converter, action_mode))
            # 递归遍历
            for (b_matched, b_popped), k, idx in zip(deal_res_ls, keys, idx_ls):
                if b_popped or (b_matched and not b_traverse_matched_element):
                    continue
                var[k] = _dfs(var[k], match_cond, action_mode, converter, b_use_name_as_idx, traversal_mode,
                              b_traverse_matched_element, idx)
        else:
            # 后序
            # 递归遍历
            for k, idx in zip(keys, idx_ls):
                var[k] = _dfs(var[k], match_cond, action_mode, converter, b_use_name_as_idx, traversal_mode,
                              b_traverse_matched_element, idx)
            # 匹配&处理
            for k, idx in zip(keys, idx_ls):
                _deal(var, k, idx, match_cond, converter, action_mode)
    else:
        pass
    return var


def _deal(var, k, idx, match_cond, converter, action_mode):
    """处理节点"""
    # 匹配
    b_matched = match_cond(type(var), idx, var[k])
    b_popped = False
    # 处理
    if b_matched:
        if action_mode is Action_Mode.REMOVE:
            var.pop(k)
            b_popped = True
        elif action_mode is Action_Mode.REPLACE:
            var[k] = converter(idx, var[k])
        else:
            pass
    return b_matched, b_popped


def _gen_idx(var, keys, b_use_name_as_idx, pre_name):
    if b_use_name_as_idx:
        idx_ls = []
        for k in keys:
            method = "@" if isinstance(var, list) or not isinstance(k, str) else ":"
            k = escape_node(node=k, b_reversed=False, times=1)
            idx_ls.append(f'{pre_name}{method}{k}')
    else:
        idx_ls = keys
    return idx_ls
