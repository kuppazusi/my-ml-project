import nbformat
import sys

notebook_path = sys.argv[1]

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# 不正なwidgetsを除去
if 'widgets' in nb.metadata:
    print(f"Removing invalid 'widgets' metadata from: {notebook_path}")
    del nb.metadata['widgets']

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
