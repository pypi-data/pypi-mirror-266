from kevin_toolbox.math.utils import split_integer_most_evenly


def generate_table(content_s, orientation="vertical", chunk_nums=None, chunk_size=None, b_allow_misaligned_values=False,
                   f_gen_order_of_values=None):
    """
        生成表格

        参数：
            content_s:              <dict> 内容
                                        支持两种输入模式：
                                            1.简易模式：
                                                content_s = {<title>: <list of value>, ...}
                                                此时键作为标题，值作为标题下的一系列值。
                                                由于字典的无序性，此时标题的顺序是不能保证的，若要额外指定顺序，请使用下面的 完整模式。
                                            2. 完整模式:
                                                content_s = {<index>: {"title": <title>,"values":<list of value>}, ...}
                                                此时将取第 <index> 个 "title" 的值来作为第 <index> 个标题的值。values 同理。
                                                该模式允许缺省某些 <index>，此时这些 <index> 对应的行/列将全部置空。
            orientation:            <str> 表格的方向
                                        支持以下值：
                                            "vertical" / "v":       纵向排列，亦即标题在第一行
                                            "horizontal" / "h":     横向排列，亦即标题在第一列
            chunk_nums:             <int> 将表格平均分割为多少份进行并列显示。
            chunk_size:             <int> 将表格按照最大长度进行分割，然后并列显示。
                注意：以上两个参数只能设置一个，同时设置时将报错
            b_allow_misaligned_values   <boolean> 允许不对齐的 values
                                        默认为 False，此时当不同标题下的 values 的长度不相等时，将会直接报错。
                                        当设置为 True 时，对于短于最大长度的 values 将直接补充 ""。
            f_gen_order_of_values:  <callable> 生成values排序顺序的函数
                                        该函数需要接受一个形如 {<title>: <value>, ...} 的 <dict>，并返回一个用于排序的 int/float/tuple
    """
    # 检验参数
    assert chunk_nums is None or 1 <= chunk_nums
    assert chunk_size is None or 1 <= chunk_size
    assert orientation in ["vertical", "horizontal", "h", "v"]

    # 将简易模式转换为完整模式
    if len(content_s.values()) > 0 and not isinstance(list(content_s.values())[0], (dict,)):
        content_s = {i: {"title": k, "values": v} for i, (k, v) in enumerate(content_s.items())}
    # 对齐 values
    len_ls = [len(v["values"]) for v in content_s.values()]
    max_length = max(len_ls)
    if min(len_ls) != max_length:
        assert b_allow_misaligned_values, \
            f'The lengths of the values under each title are not aligned. ' \
            f'The maximum length is {max_length}, but each length is {len_ls}'
        for v in content_s.values():
            v["values"].extend([""] * (max_length - len(v["values"])))
    # 对值进行排序
    if callable(f_gen_order_of_values):
        idx_ls = list(range(max_length))
        idx_ls.sort(key=lambda x: f_gen_order_of_values({v["title"]: v["values"][x] for v in content_s.values()}))
        for v in content_s.values():
            v["values"] = [v["values"][i] for i in idx_ls]
    # 补充缺省的 title
    for i in range(max(content_s.keys()) + 1):
        if i not in content_s:
            content_s[i] = {"title": "", "values": [""] * max_length}
    # 按照 chunk_nums 或者 chunk_size 对表格进行分割
    if chunk_nums is not None or chunk_size is not None:
        if chunk_nums is not None:
            split_len_ls = split_integer_most_evenly(x=max_length, group_nums=chunk_nums)
        else:
            split_len_ls = [chunk_size] * (max_length // chunk_size)
            if max_length % chunk_size != 0:
                split_len_ls += [max_length % chunk_size]
        max_length = max(split_len_ls)
        temp = dict()
        beg = 0
        for i, new_length in enumerate(split_len_ls):
            end = beg + new_length
            temp.update({k + i * len(content_s): {"title": v["title"],
                                                  "values": v["values"][beg:end] + [""] * (max_length - new_length)} for
                         k, v in content_s.items()})
            beg = end
        content_s = temp
    # 构建表格
    return _show_table(content_s=content_s, orientation=orientation)


def _show_table(content_s, orientation="vertical"):
    """
        生成表格

        参数：
            content_s:              <dict> 内容
                                        content_s = {<index>: {"title": <title>,"values":<list of value>}, ...}
                                        此时将取第 <index> 个 "title" 的值来作为第 <index> 个标题的值。values 同理。
            orientation:            <str> 表格的方向
                                        支持以下值：
                                            "vertical" / "v":       纵向排列，亦即标题在第一行
                                            "horizontal" / "h":     横向排列，亦即标题在第一列
    """
    table = ""
    if orientation in ["vertical", "v"]:
        table += "| " + " | ".join([f'{content_s[i]["title"]}' for i in range(len(content_s))]) + " |\n"
        table += "| " + " | ".join(["---"] * len(content_s)) + " |\n"
        for row in zip(*[content_s[i]["values"] for i in range(len(content_s))]):
            table += "| " + " | ".join([f'{i}' for i in row]) + " |\n"
    else:
        for i in range(len(content_s)):
            row = [f'{content_s[i]["title"]}'] + [f'{i}' for i in content_s[i]["values"]]
            table += "| " + " | ".join(row) + " |\n"
            if i == 0:
                table += "| " + " | ".join(["---"] * len(row)) + " |\n"
    return table


if __name__ == '__main__':
    content_s = {0: dict(title="a", values=[1, 2, 3]), 2: dict(title="b", values=[4, 5, 6])}
    doc = generate_table(content_s=content_s, orientation="h")
    print(doc)

    # from collections import OrderedDict
    #
    # content_s = OrderedDict({
    #     "y/n": [True] * 5 + [False] * 5,
    #     "a": list(range(10)),
    #     "b": [chr(i) for i in range(50, 60, 2)]
    # })
    # doc = generate_table(content_s=content_s, orientation="v", chunk_size=4, b_allow_misaligned_values=True,
    #                      f_gen_order_of_values=lambda x: (-int(x["y/n"] is False), -(x["a"] % 3)))
    # print(doc)
    # import os
    #
    # with open(os.path.join(
    #         "/home/SENSETIME/xukaiming/Desktop/my_repos/python_projects/kevin_toolbox/kevin_toolbox/data_flow/file/markdown/test/test_data/for_generate_table",
    #         f"data_5.md"), "w") as f:
    #     f.write(doc)
