from typing import List
from pathlib import Path
from editorCode.editorFilesystem import EditorDir



f = EditorDir('..', ['.py'])
print(f.getFolders())
print(f.getCurrentDir())
f.goDown('test1')
print(f.getCurrentDir())
print(f.getFolders())
f.goUp()
print(f.getFolders())
f.goUp()
print(f.getFolders())
print(f.getFiles())
f.goDown('KowVsBunny')
print(f.getFolders())
f.goDown('editorCode')
print(f.getFiles())
print(f.getCurrentDir())