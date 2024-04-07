import random

PREDEFINED = ['blue', 'red', 'green', 'orange', 'purple', 'yellow', "brown", "pink", "gray", "olive", "cyan"]


def generate_color_list(nums, seed=None, exclude_ls=None):
    """
        参数:
            nums:           <int> 生成颜色的数量
            seed:           随机种子
            exclude:        <list of str> 需要排除的颜色
    """
    global PREDEFINED
    if exclude_ls is None:
        exclude_ls = []
    assert isinstance(exclude_ls, (list, tuple))

    colors = [i for i in PREDEFINED if i not in exclude_ls][:nums]  # 优先输出预定义的颜色

    # 随机生成剩余数量的颜色
    if seed is not None:
        random.seed(seed)
    while len(colors) < nums:
        c = "#" + ''.join(random.choices('0123456789ABCDEF', k=6))
        if c not in colors and c not in exclude_ls:
            colors.append(c)

    return colors


if __name__ == '__main__':
    color_list = generate_color_list(20)
    print(color_list)
