from pathlib import Path
from typing import List

class EditorDir:

    def __init__(self, root:str='.', fileFilter: List[str]=[]) -> None:
        self.root = Path(root).absolute()
        self.currentPath = Path(root).absolute()
        self.fileFilter = fileFilter

    def getCurrentDir(self) -> str:
        path = ''
        try:
            path = str(self.currentPath.relative_to(self.root))
        except:
            pass
        return path

    def getFolders(self) -> List[str]:
        folders = []
        for folder in self.currentPath.iterdir():
            if folder.exists() and folder.is_dir():
                folders.append(folder.name)
        folders.sort()
        return folders
    
    def getFiles(self):
        files = []
        for file in self.currentPath.iterdir():
            if file.exists() and file.is_file():
                for filter in self.fileFilter:
                    if file.name.endswith(filter):
                        files.append(file.name)
        files.sort()
        return files
    
    def goDown(self, toFolder:str) -> bool:
        downTo = self.currentPath / toFolder
        result = False
        if downTo.exists and downTo.is_dir():
            self.currentPath = downTo
            result = True
        return result

    def getFileBytes(self, name:str) -> bytes:
        file = self.currentPath / name
        fileData = None
        if file and file.exists() and file.is_file():
            with file.open('rb') as f:
                fileData = f.read()
        return fileData

    def getFileText(self, name:str) -> str:
        file = self.currentPath / name
        fileData = None
        if file and file.exists() and file.is_file():
            with file.open('r') as f:
                fileData = f.read()
        return fileData
    
    def getFilePath(self, name:str) -> str:
        file = self.currentPath / name
        filePath = None
        if file and file.exists() and file.is_file():
            filePath = str(file)
        return filePath
    
    def getFileRelativePath(self, name:str) -> str:
        file = self.currentPath / name
        filePath = None
        if file and file.exists() and file.is_file() and file.is_relative_to(self.root):
            filePath = str(file.relative_to(self.root))
        return filePath

    def goUp(self) -> bool:
        up = self.currentPath.parent
        result = False
        try:
            # limit to root
            if up.is_relative_to(self.root):
                self.currentPath = up
                result = True
        except:
            pass
        return result