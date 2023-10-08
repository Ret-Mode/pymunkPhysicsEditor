from typing import Union
from .editorCamera import EditorCamera, CursorCamera

class GLContextI:

    _instance: "GLContextI" = None

    @staticmethod
    def getInstance() -> "GLContextI":
        assert GLContextI._instance is not None
        return GLContextI._instance

    def setProjectionAndViewportFromCamera(self, camera:Union[CursorCamera, EditorCamera]):
        raise NotImplementedError

    def getFramebufferSize(self):
        raise NotImplementedError