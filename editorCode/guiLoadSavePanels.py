from .guiButtons import Button, Label, TextInput, ScrollableLayout
from .editorFilesystem import EditorDir
from .commandExec import CommandExec, ComLoad, ComSave, ComExport
from .editorTester import Tester
import arcade.gui
from typing import List, Callable


class FileListPanel(arcade.gui.UIBoxLayout):

    def __init__(self, root:str, fileClicked:Callable[[str], None]) -> None:
        super().__init__(vertical=True)
        self.fileCB = fileClicked
        filters = ['.json', '.sv']
        self.dirIntern = EditorDir(root, filters)
        self.currentDir = Label(self.dirIntern.getCurrentDir(),'sevenEightsWidth', 'left')
        upButton = Button('Up', 'eightWidth', self.up)

        self.fileList = ScrollableLayout(max=8, callback=self.process)
        self.updateFileList()

        folderLine = arcade.gui.UIBoxLayout(vertical=False)
        folderLine.add(self.currentDir)
        folderLine.add(upButton)
        self.add(folderLine)
        self.add(self.fileList)

    def getCurrentDir(self):
        return self.currentDir.text
    
    def getFilesInFolder(self):
        return self.dirIntern.getFiles()

    def up(self):
        if self.dirIntern.goUp():
            self.updateFileList()

    def process(self, *args):
        if args:
            clickedElem = args[0]
            if clickedElem:
                if clickedElem in self.dirIntern.getFolders():
                    self.dirIntern.goDown(clickedElem)
                    self.updateFileList() 
                elif clickedElem in self.dirIntern.getFiles():
                    self.fileCB(clickedElem)
    
    def updateFileList(self):
        self.currentDir.setText(self.dirIntern.getCurrentDir())
        entries = self.dirIntern.getFolders() + self.dirIntern.getFiles()
        self.fileList.setLabels(entries)


class ButtonsPanel(arcade.gui.UIBoxLayout):
    def __init__(self, save, saveNew, load, export) -> None:
        super().__init__(vertical = False)
        saveButton = Button("Save", 'quartWidth', save)
        saveNewButton = Button("SavNew", 'quartWidth', saveNew)
        loadButton = Button("Load", 'quartWidth', load)
        exportButton = Button("Export", 'quartWidth', export)

        self.add(saveButton)
        self.add(saveNewButton)
        self.add(loadButton)
        self.add(exportButton)


class LoadSaveButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical = True)
        self.list = FileListPanel('.', self.setFileName)

        self.fileName = TextInput('')
        buttons = ButtonsPanel(self.save, self.saveNew, self.load, self.export)
        test = Button("Test", 'width', self.test)

        self.add(self.list)
        self.add(self.fileName)
        self.add(buttons)
        self.add(test)

    def test(self):
        fileName = self.getFileName()
        if '.' in fileName:
            fileName = fileName[:fileName.rfind('.')]
        if len(fileName) < 1:
            return
        fileName += '.json'
        Tester.getInstance().execute("test.py")

    def setFileName(self, filename:str):
        self.fileName.setText(filename)

    def getFileName(self) -> str:
        return self.fileName.text

    def save(self):
        fileName = self.getFileName()
        if '.' in fileName:
            fileName = fileName[:fileName.rfind('.')]
        if len(fileName) < 1:
            return
        fileName += '.sv'
        CommandExec.getInstance().addCommand(ComSave(self.list.getCurrentDir() + '/' + fileName))

    def saveNew(self):
        fileName = self.getFileName()
        if '.' in fileName:
            fileName = fileName[:fileName.rfind('.')]
        if len(fileName) < 1:
            return
        otherFiles = self.list.getFilesInFolder()
        filePostfix = 0

        newFileName = fileName + '.sv'
        while newFileName in otherFiles:
            filePostfix += 1
            newFileName = fileName + f'_{filePostfix}.sv'
        CommandExec.getInstance().addCommand(ComSave(self.list.getCurrentDir() + '/' + newFileName))

    def load(self):
        fileName = self.getFileName()
        if '.' in fileName:
            fileName = fileName[:fileName.rfind('.')]
        if len(fileName) < 1:
            return
        fileName += '.sv'
        CommandExec.getInstance().addCommand(ComLoad(self.list.getCurrentDir() + '/' + fileName))

    def export(self):
        fileName = self.getFileName()
        if '.' in fileName:
            fileName = fileName[:fileName.rfind('.')]
        if len(fileName) < 1:
            return
        fileName += '.json'
        CommandExec.getInstance().addCommand(ComExport(self.list.getCurrentDir() + '/' + fileName))
