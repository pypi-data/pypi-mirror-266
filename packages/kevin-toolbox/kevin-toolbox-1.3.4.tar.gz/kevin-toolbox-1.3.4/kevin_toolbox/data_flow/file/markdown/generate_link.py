def generate_link(name, target, type_="url"):
    assert type_ in ["url", "image"]
    return f'{"!" if type_ == "image" else ""}[{name}]({target})'


if __name__ == '__main__':
    print(generate_link(name=444, target="233", type_="url"))
    print(generate_link(name=444, target="233", type_="image"))
