def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
    return tree
