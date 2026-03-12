import os

def parse_tree(text:str):
    lines = text.splitlines()
    root = {}
    stack = [(-1, root)]
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        name = line.strip()

        while stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        # directory
        if name.endswith("/"):
            name = name[:-1]
            parent[name] = {}
            stack.append((indent, parent[name]))
            i += 1
            continue

        # file with content
        if name.endswith(":"):
            filename = name[:-1]
            content = []
            i += 1

            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    content.append("")
                    i += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip())

                if next_indent <= indent:
                    break

                content.append(next_line.strip())
                i += 1

            parent[filename] = "\n".join(content)
            continue

        # empty file
        parent[name] = None
        i += 1

    return root


def create_fs(tree:dict, base="."):
    for name, value in tree.items():
        path = os.path.join(base, name)

        if isinstance(value, dict):
            os.makedirs(path, exist_ok=True)
            create_fs(value, path)

        else:
            with open(path, "w", encoding="utf8") as f:
                if value:
                    f.write(value)


# ---- usage ----
def execute(filepath:str,folderpath):
    if os.path.exists(filepath):
        if filepath.endswith('.fstree'):
            with open(filepath) as f:
                txt = f.read()

            tree = parse_tree(txt)

            create_fs(tree, folderpath)
            return (True,'')
        return (False,f'{filepath} not .fstree file')    
    return (False,f'{filepath} not exist')
