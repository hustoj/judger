def write_file(name, content):
    with open(name, 'w') as f:
        f.write(content)


def get_file_content(path):
    with open(path) as f:
        return f.read()