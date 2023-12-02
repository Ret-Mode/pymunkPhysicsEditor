# Pymunk Physics Editor

Physics editor to Pymunk, written in Python, using Arcade library.

Currently application is in **heavy** development and is actually not usable.
Missing features (ordered somewhat as they are planned to be developed):

- [x] One draw call of shapes per view per frame
- [x] Corrections of the draw call chain
- [x] Adding background grid
- [x] Generate grid on GPU as it was the slowest action to perform
- [x] Texture mapping:
   - [x] Add file select panel restricted to game directory
   - [x] Add texture view
   - [x] Add mapping of textures to bodies
   - [x] Add texture shader
- [x] Add transforms to texture views
- [x] Add constraints to simple loader
- [x] Saving/loading (JSON)
- [x] Supporting all parameters of pymunk objects (without a radius)
- [ ] Add possibility of changing a shape radius
- [ ] Cloning of objects
- [ ] Additional buttons (CoG to Pivot, etc)
- [ ] Snapping to points
- [ ] Add GL texture loader
- [ ] Change transform panel (remove update)
- [ ] Fix pickling (default save method i guess - move mappings and textures to the database)
- [ ] Add texture utils and options (mipmaps, filtering, etc)
- [ ] Lock mouse on transforms
- [ ] Add transforms and textures to constraints view
- [ ] Support for convex polygons
- [ ] Support skewing
- [ ] Snapping to edges
- [ ] Adjusting GUI
- [ ] Support for higher versions of Arcade / other libraries
- [ ] Support for other 2d engines
- [ ] Adding documentation

