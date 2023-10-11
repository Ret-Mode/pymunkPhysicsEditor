import arcade.gui

from typing import List, Callable, Tuple

from .database import Database
from .editorState import EditorState
from .shapeInternals.editorBodyI import BodyI
from .guiButtons import ScrollableLayout, TexturePreview
from .guiButtons import Button, Label
from .guiPanels import ScrollableCBLabelPanel, ScrollableConstantPanel, EmptyPanel
from .config import physicsSetup
from .editorFilesystem import EditorDir
from .textureContainerI import TextureContainerI
from .textureMapping import TextureMapping
from .editorState import EditorState

# FILE PANELS
class SetTextureToChannelPanel(arcade.gui.UIBoxLayout):
    
    def __init__(self, assignTexToChannel:Callable):
        super().__init__(vertical=True)
        row = arcade.gui.UIBoxLayout(vertical=False)
        self.assignTexToChannel = assignTexToChannel
        self.assignButton = Button('Assign to:', 'halfWidth', self.assign)
        self.channels = ScrollableConstantPanel(list(map(str, [i for i in range(16)])), 'eightWidth', 'quartWidth')
        currentlyAssigned = Label('Currently assigned to this channel:', align='left')
        self.currentPath = Label('...nothing ', align='right')
        row.add(self.assignButton)
        row.add(self.channels)
        self.add(row)
        self.add(currentlyAssigned)
        self.add(self.currentPath)

    def assign(self):
        currentChannel = int(self.channels.getCurrent())
        if currentChannel >= 0 and currentChannel <= 15:
            self.assignTexToChannel(currentChannel)

    def on_update(self, dt):
        retVal = super().on_update(dt)
        currentChannel = int(self.channels.getCurrent())
        container = TextureContainerI.getInstance()
        path = container.getPath(currentChannel)
        if path:
            self.currentPath.setText(path)
        else:
            self.currentPath.setText('...nothing ')
        return retVal


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
        self.assignChannel = SetTextureToChannelPanel(self.assignToChannel)
        self.preview = TexturePreview()

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
        if self.preview.originalFilePath:
            size = self.preview.getTextureSize()
            container = TextureContainerI.getInstance()
            container.load(self.preview.originalFilePath, toChannel, size)
            database = Database.getInstance()
            for mapping in database.getAllMappingsOfChannel(toChannel):
                mapping.initialize(size)

# end of FILE PANELS


# MAPPING PANELS

class MappingDetailsPanel(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)


class BodySelectPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical=False)
        label = Label("Body", width='quartWidth', align='left')
        self.currentBody = ScrollableCBLabelPanel('--', lrWidth='quartWidth', labelWidth='quartWidth', cbNext=self.next, cbPrev=self.prev)
        self.currentMapping:TextureMapping = None
        self.add(label)
        self.add(self.currentBody)

    def next(self):
        database = Database.getInstance()
        if self.currentMapping:
            current = self.currentMapping.body.label if self.currentMapping.body else '--'
        labels = database.getAllBodyLabels()
        if current in labels:
            indexOfBody = labels.index(current)
            label = labels[(indexOfBody + 1)%len(labels)]
        elif labels:
            label = labels[0]
        else:
            label = '--'
        body = database.getBodyByLabel(label)
        if body:
            self.currentMapping.setBody(body)

    def prev(self):
        database = Database.getInstance()
        if self.currentMapping:
            current = self.currentMapping.body.label if self.currentMapping.body else '--'
        labels = database.getAllBodyLabels()
        if current in labels:
            indexOfBody = labels.index(current)
            label = labels[(indexOfBody + 1 + len(labels))%len(labels)]
        elif labels:
            label = labels[-1]
        else:
            label = '--'
        body = database.getBodyByLabel(label)
        if body:
            self.currentMapping.setBody(body)

    def updateDetails(self):
        pass

    def on_update(self, dt):
        retVal = super().on_update(dt)
        mapping = EditorState.getInstance().getCurrentMapping()
        if self.currentMapping != mapping:
            self.currentMapping = mapping
            self.updateDetails()
        if self.currentMapping and self.currentMapping.body:
            self.currentBody.setLabel(self.currentMapping.body.label)
        else:
            self.currentBody.setLabel('--')

        return retVal


class MappingsPanel(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)  
        
        upperLine = arcade.gui.UIBoxLayout(vertical = False)
        addButton = Button('Add', 'quartWidth', self.addMapping)
        self.currentChannelLine = ScrollableCBLabelPanel('--', lrWidth='quartWidth', labelWidth='quartWidth', cbNext=self.next, cbPrev=self.prev)
        self.currentChannelPath = Label('--', align='left')
        self.mappings = ScrollableLayout(max=8, callback=self.loadMapping)

        self.mappingDetails = BodySelectPanel()
        self.empty = EmptyPanel('Select mapping')

        self.currentPanel = self.empty

        upperLine.add(addButton)
        upperLine.add(self.currentChannelLine)

        self.add(upperLine)
        self.add(self.currentChannelPath)
        self.add(self.mappings)
        self.add(self.currentPanel)

    def addMapping(self):
        textures = TextureContainerI.getInstance()
        current = textures.getCurrent()
        if current is not None:
            database = Database.getInstance()
            mapping = database.createMapping(current, textures.getSize(current))
            database.addMapping(mapping)
            #textures.addMapping(mapping)
            self.mappings.setLabels(database.getAllMappingLabelsOfChannel(current))

    def prev(self):
        textures = TextureContainerI.getInstance()
        textures.setPrev()
        current = textures.getCurrent()
        if current is not None:
            database = Database.getInstance()
            self.currentChannelLine.setLabel(str(current))
            self.currentChannelPath.setText(textures.getCurrentPath())
            self.mappings.setLabels(database.getAllMappingLabelsOfChannel(current))
        else:
            self.currentChannelLine.setLabel('--')
            self.currentChannelPath.setText('--')
            self.mappings.setLabels([])

    def next(self):
        textures = TextureContainerI.getInstance()
        textures.setNext()
        current = textures.getCurrent()
        if current is not None:
            database = Database.getInstance()
            self.currentChannelLine.setLabel(str(current))
            self.currentChannelPath.setText(textures.getCurrentPath())
            self.mappings.setLabels(database.getAllMappingLabelsOfChannel(current))
        else:
            self.currentChannelLine.setLabel('--')
            self.currentChannelPath.setText('--')
            self.mappings.setLabels([])

    def loadMapping(self, label):
        textures = TextureContainerI.getInstance()
        currentChannel = textures.getCurrent()
        if currentChannel is not None:
            state = EditorState.getInstance()
            state.setCurrentMappingByLabel(label)
            mapping = state.getCurrentMapping()
            if mapping:
                if self.currentPanel == self.empty:
                    self.remove(self.currentPanel)
                    self.currentPanel = self.mappingDetails
                    self.add(self.currentPanel)
            else:
                if self.currentPanel == self.mappingDetails:
                    self.remove(self.currentPanel)
                    self.currentPanel = self.empty
                    self.add(self.currentPanel)
        else:
            if self.currentPanel == self.mappingDetails:
                self.remove(self.currentPanel)
                self.currentPanel = self.empty
                self.add(self.currentPanel)

# end of MAPPING PANELS

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
