from pathlib import Path
from urllib.request import urlretrieve

folder = Path("js_lib_editor_js/static/editorjs/")

prefix = "https://cdn.jsdelivr.net/npm/@editorjs/"

version = "2.29.1"

pkgs = f"""
editorjs@{version}
paragraph
image
header
list
checklist
quote
raw
code
inline-code
embed
delimiter
warning
link
marker
table
""".strip().splitlines()

if __name__ == '__main__':
    # fetch and save to folder
    for pkg in pkgs:
        url = prefix + pkg
        base = pkg
        if "@" in base:
            base = base[:base.index("@")]
        p = folder / (base + ".js")
        urlretrieve(url, p)
        kb = p.stat().st_size // 1024
        print(f"{pkg}: {kb}kb")
