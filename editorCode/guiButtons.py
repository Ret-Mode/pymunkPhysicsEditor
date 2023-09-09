from typing import Optional, List, Callable, Any
import arcade.gui
from arcade.gui.events import UIEvent, UIOnClickEvent, UITextEvent, UIKeyPressEvent
from arcade.gui.surface import Surface
from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

from .guiTimeMeasure import TimeMeasure
from .config import editorButtonSetup



class CheckVar:
    def __init__(self) -> None:
        self.v = False

    def get(self) -> bool:
        return self.v
    
    def swap(self) -> None:
        self.v = not self.v


class CheckButton(arcade.gui.UIFlatButton):

    def __init__(self, text: str = '', onText:str = 'V', offText:str = 'X', width: str = 'width', default:bool = False, cb=None) -> None:
        super().__init__(text=text, 
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'], 
                        style=editorButtonSetup['style'])
        self.isOn: bool = default
        self.thisText: str = text
        self.onText = onText
        self.offText = offText
        self._cb = cb
        boolText = (self.onText if self.isOn else self.offText)
        self.text = f'{self.thisText}:{boolText}' if self.thisText else f'{boolText}'
        self.on_click = self.swap

    def swap(self, *args):
        self.isOn = not self.isOn
        boolText = (self.onText if self.isOn else self.offText)
        self.text = f'{self.thisText}:{boolText}' if self.thisText else f'{boolText}'
        if self._cb:
            self._cb(self.isOn)


class IndexButton(arcade.gui.UIFlatButton):

    def __init__(self, text: str, width: str = 'width', callback=None, index: int = 0) -> None:
        super().__init__(text=text, 
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'], 
                        style=editorButtonSetup['style'])
        self._callback = callback
        self._index: int = index

    def on_click(self, event: UIOnClickEvent) -> None:
        self._callback(self, self._index)


class TextButton(arcade.gui.UIFlatButton):

    def __init__(self, text: str, width: str = 'width', callback=None):
        super().__init__(text=text, 
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'], 
                        style=editorButtonSetup['style'])
        self._callback = callback

    def on_click(self, event: UIOnClickEvent):
        self._callback(self.text)


class Button(arcade.gui.UIFlatButton):

    def __init__(self, text: str, width: str = 'width', callback=None) -> None:
        super().__init__(text=text, 
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'], 
                        style=editorButtonSetup['style'])
        self._callback = callback

    def on_click(self, event: UIOnClickEvent) -> None:
        if self._callback:
            self._callback()


class ScrollableLayout(arcade.gui.UIBoxLayout):

    def __init__(self, max: int, callback) -> None:
        super().__init__(vertical=True)

        self.labels: List[str] = []
        self.entries: List[TextButton] = []
        self.current: int = 0
        self._callback = callback
        self.addButtons(max)

    def addButtons(self, max: int) -> None:
        for i in range (max):
            button: TextButton = TextButton(text='--',
                            width='width', 
                            callback=self.clicked)
            self.entries.append(self.add(button))

    def clicked(self, *arg) -> None:
        self._callback(*arg)

    def recalc(self) -> None:
        for i in range(len(self.entries)):
            j: int = i + self.current
            if j < len(self.labels):
                self.entries[i].text = self.labels[j]
            else:
                self.entries[i].text = '--'
        self.trigger_full_render()

    def labelInList(self, label: str) -> bool:
        return label in self.labels

    def addLabel(self, label: str) -> None:
        if not self.labelInList(label):
            self.labels.append(label)
            self.recalc()

    def delLabel(self, label: str) -> None:
        if self.labelInList(label):
            self.labels.remove(label)
            self.recalc()

    def moveLabelUp(self, label: str) -> None:
        if self.labelInList(label):
            ind = self.labels.index(label)
            if ind > 0:
                self.labels[ind-1], self.labels[ind] = self.labels[ind], self.labels[ind-1]
                self.recalc()

    def moveLabelDown(self, label: str) -> None:
        if self.labelInList(label):
            ind = self.labels.index(label)
            if ind >= 0 and ind < len(self.labels) - 1:
                self.labels[ind+1], self.labels[ind] = self.labels[ind], self.labels[ind+1]
                self.recalc()  

    def setLabels(self, labels: List[str]) -> None:
        self.labels = labels
        self.current = 0
        self.recalc()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, arcade.gui.events.UIMouseScrollEvent):
            if len(self.labels) > 0:
                if self.rect.collide_with_point(event.x, event.y):
                    if event.scroll_y > 0 and self.current > 0:
                        self.current -= 1
                        self.recalc()
                    elif event.scroll_y < 0 and (self.current < len(self.labels) - 1):
                        self.current += 1
                        self.recalc()
            else:
                self.current = 0

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED


class ScrollableSelector(arcade.gui.UIBoxLayout):

    def __init__(self, callback) -> None:
        super().__init__(vertical=True)
        self.button: TextButton = TextButton(text='--',
                            width='width', 
                            callback=self.clicked)
        self.add(self.button)
        self.labels: List[str] = []
        self.current: int = 0
        self._callback = callback

    def clicked(self, *arg) -> None:
        if self.labels:
            self._callback(self.button.text)

    def recalc(self) -> None:
        toSet = '--'
        if len(self.labels) > 0:
            toSet = self.labels[self.current]
        if self.button.text != toSet:
            self.button.text = toSet
            self.trigger_full_render()

    def labelInList(self, label: str) -> bool:
        return label in self.labels

    def setLabels(self, labels: List[str]) -> None:
        if len(self.labels) > 0:
            oldEntry = self.button.text
            self.labels = labels
            if oldEntry in self.labels:
                self.current = self.labels.index(oldEntry)
            else:
                self.current = 0
                self.recalc()
        else:
            self.labels = labels
            self.current = 0
            self.recalc()

    def setCurrent(self, new:str):
        if new in self.labels:
            self.current = self.labels.index(new)
            self.recalc()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, arcade.gui.events.UIMouseScrollEvent):
            if len(self.labels) > 0:
                if self.rect.collide_with_point(event.x, event.y):
                    if event.scroll_y > 0:
                        self.current = (self.current - 1 + len(self.labels)) % len(self.labels)
                        self.recalc()
                        self._callback(self.button.text)
                    elif event.scroll_y < 0:
                        self.current = (self.current + 1 ) % len(self.labels)
                        self.recalc()
                        self._callback(self.button.text)
            self.recalc()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED


class ScrollableCBLabel(arcade.gui.UIBoxLayout):

    def __init__(self, label:str ='--', width='width', cbNext:Callable[[None], None]=None, cbPrev:Callable[[None], None] = None) -> None:
        super().__init__(vertical=True)
        self.text: Label = Label(text=label,
                            width=width)
        self.add(self.text)
        self.cbNext:Callable[[None], None] = cbNext
        self.cbPrev:Callable[[None], None] = cbPrev

    def setLabel(self, label:str) -> None:
        if self.text.text != label:
            self.text.text = label

    def getCurrent(self) -> str:
        return self.text.text

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, arcade.gui.events.UIMouseScrollEvent):
            if self.rect.collide_with_point(event.x, event.y):
                if event.scroll_y > 0 and self.cbPrev:
                    self.cbPrev()
                elif event.scroll_y < 0 and self.cbNext:
                    self.cbNext()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED
    

class ScrollableConstant(arcade.gui.UIBoxLayout):

    def __init__(self, labels: List[str] = [], width='width') -> None:
        super().__init__(vertical=True)
        self.text: Label = Label(text='--',
                            width=width)
        if labels:
            self.text.text = labels[0]
        self.add(self.text)
        self.labels: List[str] = labels
        self.current: int = 0

    def setLabels(self, labels: List[str]) -> None:
        self.labels = labels
        self.current = 0

    def getCurrent(self) -> str:
        return self.text.text

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if len(self.labels) > 0:
            if isinstance(event, arcade.gui.events.UIMouseScrollEvent):
                if self.rect.collide_with_point(event.x, event.y):
                    if event.scroll_y > 0:
                        self.current = (self.current - 1 + len(self.labels)) % len(self.labels)
                        self.text.text = self.labels[self.current]
                    elif event.scroll_y < 0:
                        self.current = (self.current + 1 ) % len(self.labels)
                        self.text.text = self.labels[self.current]

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED
    

class Label(arcade.gui.UILabel):
    def __init__(self, text: str, width:str = 'width', align: str = 'center') -> None:
        super().__init__(text=text, 
                        font_size=editorButtonSetup['style']['font_size'],
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'], 
                        style=editorButtonSetup['style'],
                        align=align)


class TextInput(arcade.gui.UIInputText):

    def __init__(self, text: str, width: str = 'width', callback: Callable[[Any], None]=print):
        super().__init__(text=text, 
                        font_size=editorButtonSetup['style']['font_size'],
                        text_color=(255, 255, 255, 255),
                        width=editorButtonSetup[width], 
                        height=editorButtonSetup['height'])
        self.caret.color = (255,255,255)
