import arcade.gui
from arcade.texture import Texture

from typing import List, Callable, Tuple

from .guiButtons import ScrollableLayout, TexturePreview, ScrollableConstant
from .guiButtons import Button, Label
from .guiPanels import ScrollableCBLabelPanel
from .config import physicsSetup
from .editorFilesystem import EditorDir
from .arcadeTextureContainer import ArcadeTexture


class SetTextureToChannelPanel(arcade.gui.UIBoxLayout):
    
    def __init__(self, assignTexToChannel:Callable):
        super().__init__(vertical=False)
        self.assignTexToChannel = assignTexToChannel

        self.assignButton = Button('Assign to:', 'halfWidth', self.assign)
        self.channels = ScrollableConstant(list(map(str, [i for i in range(16)])), 'halfWidth')

        self.add(self.assignButton)
        self.add(self.channels)

    def assign(self):
        currentChannel:int = -1
        try:
            currentChannel = int(self.channels.getCurrent())
        except:
            pass
        if currentChannel >= 0 and currentChannel <= 15:
            self.assignTexToChannel(currentChannel)


class TextureSizeIntPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical=False)
        label = Label('Size', 'thirdWidth', 'left')
        self.xPanel = Label('0', 'thirdWidth', 'left')
        self.yPanel = Label('0', 'thirdWidth', 'left')
        
        self.add(label)
        self.add(self.xPanel)
        self.add(self.yPanel)
    
    def setSize(self, size:Tuple[int]):
        try:
            self.xPanel.setText(str(size[0]))
            self.yPanel.setText(str(size[1]))
        except:
            self.xPanel.setText('0')
            self.yPanel.setText('0')


class TextureListPanel(arcade.gui.UIBoxLayout):

    def __init__(self, root:str, textureClicked:Callable[[str], None]) -> None:
        super().__init__(vertical=True)
        filters = ['.jpg', '.jpeg', '.png', '.bmp']
        self.textureCB = textureClicked
        
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
                    self.textureCB(self.dirIntern.getFileRelativePath(clickedElem))
    
    def updateFileList(self):
        self.currentDir.setText(self.dirIntern.getCurrentDir())
        entries = self.dirIntern.getFolders() + self.dirIntern.getFiles()
        self.fileList.setLabels(entries)


class TextureSelectPanel(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(4)]
        self.textureListPanel = TextureListPanel('.', textureClicked=self.loadPreview)
        self.sizePanel = TextureSizeIntPanel()
        self.preview = TexturePreview()
        self.assignChannel = SetTextureToChannelPanel(self.assignToChannel)

        self.rows[0].add(self.textureListPanel)
        self.rows[1].add(self.sizePanel)
        self.rows[2].add(self.assignChannel)
        self.rows[3].add(self.preview)

    def loadPreview(self, path):
        self.preview.loadTextureFromPath(path)
        self.sizePanel.setSize(self.preview.getTextureSize())

    def assignToChannel(self, toChannel:int):
        # TODO add command when other functionality is ready
        # to reconsider moving this into command - file op, what if file is deleted?
        ArcadeTexture.getInstance().load(self.preview.originalFilePath, toChannel)


class MappingsPanel(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)   
        self.add(ScrollableCBLabelPanel('--'))

        mappings = ScrollableLayout(max=8, callback=self.loadMapping)
        self.add(mappings)

    def loadMapping(self, *args):
        pass


class TextureButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)
        
        self.mainButtonLine = arcade.gui.UIBoxLayout(vertical=False)
        textureButton = Button('FILE', 'halfWidth', self.activateTexturePanel)
        mappingButton = Button('MAPPING', 'halfWidth', self.activateMappingPanel)
        self.mappingPanel = MappingsPanel()
        self.texturePanel = TextureSelectPanel()
        self.current = self.texturePanel

        self.mainButtonLine.add(textureButton)
        self.mainButtonLine.add(mappingButton)
        self.add(self.mainButtonLine)
        self.add(self.current)

    def activateTexturePanel(self):
        if self.current != self.texturePanel:
            self.remove(self.current)
            self.current = self.texturePanel
            self.add(self.current)
            
    def activateMappingPanel(self):
        if self.current != self.mappingPanel:
            self.remove(self.current)
            self.current = self.mappingPanel
            self.add(self.current)
    
    def on_update(self, dt):
        retVal = super().on_update(dt)
        
        return retVal
