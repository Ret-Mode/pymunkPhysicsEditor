from .editorTypes import V2


class Cursor:

    _instance: "Cursor" = None

    @staticmethod
    def getInstance() -> "Cursor":
        if Cursor._instance is None:
            Cursor._instance = Cursor()
        return Cursor._instance

    def __init__(self) -> None:
        self.screenCoords: V2 = V2()
        self.viewCoords: V2 = V2()
