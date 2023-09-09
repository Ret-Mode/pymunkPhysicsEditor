import arcade.gui

from typing import List

from .guiButtons import CheckButton
from .config import physicsSetup

class OptionsButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(1)]

        self.rows[0].add(CheckButton(text="Pixels", width='thirdWidth', default=True, cb = self.changeMeasure))
        self.rows[0].add(CheckButton(text="Pixels", width='thirdWidth', default=True, cb = self.changeMeasure))
        self.rows[0].add(CheckButton(text="Pixels", width='thirdWidth', default=True, cb = self.changeMeasure))
        
    def changeMeasure(self, value:bool):
        physicsSetup['measureInPixels'] = value

    def setCommandPipeline(self, commands):
        self.commands = commands

    def on_update(self, dt):
        retVal = super().on_update(dt)
        
        return retVal
