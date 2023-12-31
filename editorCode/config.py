import math

import json

app = {'version': '0.0.2'} 

physicsSetup = {'pixelPerMeter': 32.0,
                'measureInPixels': True}

globalWindowSetup = {'width': 800, 
                     'height': 600,
                     'title': 'Pymunk Physics Editor',
                     'fullscreen': False,
                     'resizable': True,
                     'update_rate': 1.0 / 60.0,
                     'antialiasing': False,
                     'vsync': True}

editorButtonSetup = {'width': 240,
                     'sevenEightsWidth': 210,
                     'fiveSixthWidth': 200,
                     'twoThirdsWidth': 160,
                     'halfWidth': 120,
                     'fiveTwelvthWidth': 100,
                     'thirdWidth': 80,
                     'quartWidth': 60,
                     'sixthWidth': 40,
                     'eightWidth': 30,
                     'tvelveWidth': 20,
                     'sixteenthWidth': 15,
                     'height': 20,
                     'style': {"font_size": 10} }

pointConfig = {'pointHalfWH':  3,
               'inactivePointColor': (100, 100, 100, 255),
               'activePointColor': (200, 200, 200, 255),
               'inactiveEdgeColor': (75,75,75, 255),
               'activeEdgeColor': (255,200,100, 255),
               'activeDynamicEdgeColor': (200,255,100, 255),
               'activeStaticEdgeColor': (255,100,100, 255),
               'underCursorEdgeColor': (160,150,100, 255),
               'anchorColor': (150,150,250, 255),
               'secondaryBodyColor': (170,120,100, 255),
               'grooveColor': (150,250,150, 255),
               'armLength' : 40.0,
               'ratchetArmLength' : 30.0,
               'cursorHalfWH': 5.0,
               'cursorLineColor': (93, 138, 168, 255),
               'cursorLineMenuColor': (255, 0, 0, 255),
               'helperHalfWH': 4.0,
               'helperColor': (255, 100, 100, 255),
               'anchorHalfWH': 3.0,
               'anchorColor': (100,100,200, 255),
               'cogHalfWH': 3.0,
               'cogColor': (200,100,100, 255),
               'transformArmLength': physicsSetup['pixelPerMeter'],
               'transformColor': (150,200,150, 255)}


def toJSON(data: dict) -> str:
    assert 'config' not in data
    data['config'] = {'pxPerMeter' : physicsSetup['pixelPerMeter']}
    return json.dumps(data, indent=4)


def fromJSON(data:str) -> dict:
    return json.loads(data)


def hexToString(value:int, default:str) -> str:
    try:
        return f'{value:X}'
    except:
        return default


def hexFromString(value: str, default:int) -> float:
    try:
        return int(value, 16)
    except:
        return default


def intToString(value:int, default:str) -> str:
    try:
        return f'{value}'
    except:
        return default


def intFromString(value: str, default:int) -> float:
    try:
        return int(value)
    except:
        return default
    

def floatToString(value:float, default:str) -> str:
    try:
        return f'{value:.3f}'
    except:
        return default


def floatFromString(value: str, default:float) -> float:
    try:
        return float(value)
    except:
        return default


def angleToString(angle: float, default:str) -> str:
    try:
        value = angle * 180.0 / math.pi
        return f'{value:.3f}'
    except:
        return default


def angleFromString(angle: str, default:float) -> float:
    try:
        value = float(angle) * math.pi / 180.0
        return value
    except:
        return default
    

def scaleToString(scale: float, default:str) -> str:
    try:
        return f'{scale:.6f}'
    except:
        return default


def scaleFromString(scale: str, default:float) -> float:
    try:
        return float(scale)
    except:
        return default


def distanceInPixelsToString(distance: float, default:str) -> str:
    try:
        return f'{distance:.3f}'
    except:
        return default


def distanceInStringToPixels(distance: str, default:float) -> float:
    try:
        return  float(distance)
    except:
        return default
    

def areaInPixelsToString(area: float, default:str) -> str:
    try:
        return f'{area:.3f}'
    except:
        return default


def areaInStringToPixels(area: str, default:float) -> float:
    try:
        return float(area)
    except:
        return default


def massInPixelsToString(mass: float, default:str) -> str:
    try:
        return f'{mass:.3f}'
    except:
        return default


def massInStringToPixels(mass: str, default:float) -> float:
    try:
        value = float(mass)
        return value
    except:
        return default

def momentInPixelsToString(moment: float, default:str) -> str:
    try:
        return f'{moment:.3f}'
    except:
        return default


def momentInStringToPixels(moment: str, default:float) -> float:
    try:
        value = float(moment)
        return value
    except:
        return default
    
def densityInPixelsToString(density: float, default:str) -> str:
    try:
        return f'{density:.3f}'
    except:
        return default


def densityInStringToPixels(density: str, default:float) -> float:
    try:
        return float(density)
    except:
        return default