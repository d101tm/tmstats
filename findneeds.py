#!/usr/bin/env python3
""" Find missing modules """
import sys, re, importlib, subprocess

def addto(imports, what):
    what = what.split('.')[0]
    if what not in imports:
        try:
            importlib.import_module(what)
        except ModuleNotFoundError:
            info = sys.exc_info()[1]
            imports.add(info.name)


imports = set()
cmd = r"grep -h 'import ' *.py | sed -e 's/#.*//' -e 's/ as .*//' -e 's/,/ /g'"
ans = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.split('\n')
for line in ans:
    line = line.strip()
    if line.startswith('from'):
        addto(imports, line.split()[1])
    elif line.startswith('import'):
        for mod in line.split()[1:]:
            addto(imports, mod)

print('\n'.join(sorted(imports, key=str.lower)))

