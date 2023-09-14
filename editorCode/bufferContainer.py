from typing import List

class BufferContainer:

    _instance: "BufferContainer" = None

    @staticmethod
    def getInstance() -> "BufferContainer":
        if BufferContainer._instance == None:
            BufferContainer._instance = BufferContainer()
        return BufferContainer._instance
    
    def __init__(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.colors: List[int] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def reset(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.colors: List[int] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0