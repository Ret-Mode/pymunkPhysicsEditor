from .arcadeGlContext import ArcadeGLContext
from .arcadeTextureContainer import ArcadeTexture

def arcadeInit():
    #init arcade specific code
    ArcadeGLContext.getInstance()
    ArcadeTexture.getInstance()
