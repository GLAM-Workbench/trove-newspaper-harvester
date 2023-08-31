from pathlib import Path
import json
import re
import importlib.util
import os.path
import sys

external_imports = ['jupyterlab', 'voila', 'voila-material @ git+https://github.com/GLAM-Workbench/voila-material.git']

python_path = os.path.dirname(sys.executable).replace('bin', 'lib')
#print(python_path)

imports = []
for nb in Path(__file__).resolve().parent.parent.glob('*.ipynb'):
    if not nb.name.startswith('.') and not nb.name.startswith('Untitled'):
        nb_json = json.loads(nb.read_bytes())
        for cell in nb_json['cells']:
            for line in cell['source']:
                if match := re.search(r'^\s*import ([a-zA-Z_]+)(?! from)', line):
                    imports.append(match.group(1))
                elif match := re.search(r'^\s*from ([a-zA-Z_]+)\.?[a-zA-Z_]* import [a-zA-Z_]+', line):
                    imports.append(match.group(1))

# print(list(set(imports)))

for imported_mod in list(set(imports)):
    try:
        module_path = importlib.util.find_spec(imported_mod).origin
    except AttributeError:
        pass
    else:
        if module_path:
            # print(imported_mod)
            # print(module_path)
            if 'site-packages' in module_path or python_path in module_path:
                external_imports.append(imported_mod)
    #print(external_imports)

with Path(Path(__file__).resolve().parent.parent, 'requirements-tocheck.in').open('w') as req_file:
    for mod in external_imports:
        req_file.write(mod + '\n')
