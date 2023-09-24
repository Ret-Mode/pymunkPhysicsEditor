import arcade.gui
from arcade.texture import Texture

from typing import List, Callable

from .guiButtons import ScrollableLayout, TexturePreview
from .guiButtons import Button, Label
from .config import physicsSetup
from .editorFilesystem import EditorDir


class TextureSelectPanel(arcade.gui.UIBoxLayout):

    def __init__(self, root:str, textureClicked:Callable[[str], None]) -> None:
        super().__init__(vertical=True)
        filters = ['.jpg', '.jpeg', '.png', '.bmp']
        self.textureCB = textureClicked
        self.dirIntern = EditorDir(root, filters)

        folderLine = arcade.gui.UIBoxLayout(vertical=False)
        self.currentDir = Label(self.dirIntern.getCurrentDir(),'sevenEightsWidth', 'left')

        upButton = Button('Up', 'eightWidth', self.up)

        self.fileList = ScrollableLayout(max=8, callback=self.process)
        self.updateFileList()

        folderLine.add(self.currentDir)
        folderLine.add(upButton)
        self.add(folderLine)
        self.add(self.fileList)

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
                    self.textureCB(self.dirIntern.getFilePath(clickedElem))
    
    def updateFileList(self):
        self.currentDir.setText(self.dirIntern.getCurrentDir())
        entries = self.dirIntern.getFolders() + self.dirIntern.getFiles()
        self.fileList.setLabels(entries)


class TextureButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(2)]
        self.textureSelectPanel = TextureSelectPanel('.', textureClicked=self.loadPreview)
        self.preview = TexturePreview()

        self.rows[0].add(self.textureSelectPanel)
        self.rows[1].add(self.preview)

    def loadPreview(self, path):
        self.preview.loadTextureFromPath(path)
