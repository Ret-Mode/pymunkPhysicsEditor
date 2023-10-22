from typing import Dict
from .database import Database
from .textureContainerI import TextureContainerI
import json

class JSONIO:

    @staticmethod
    def save(path:str):
        tmp = {}
        bodies = {}
        db = Database.getInstance()
        for body in db.bodies:
            body.updatePos(body.transform.getMat())
            body.recalcPhysics()
            body.getJSONDict(bodies)
        constraints = {}
        for constraint in db.constraints:
            if constraint.bodyA and constraint.bodyB:
                constraint.getJSONDict(constraints)
        mappings = {}
        for mapping in db.mappings:
            mapping.update()
            mapping.getJSONDict(mappings)
        textures = {}
        TextureContainerI.getInstance().getJSONDict(textures)
        tmp['Bodies'] = bodies
        tmp['Constraints'] = constraints 
        tmp['Mappings'] = mappings
        tmp['Textures'] = textures
        tmp['Version'] = "0.1.0"
        with open(path, 'w') as f:
            f.write(json.dumps(tmp, indent=2))


