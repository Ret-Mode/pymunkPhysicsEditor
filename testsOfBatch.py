from editorCode.batch import drawHelperPoint, drawCircle, drawCircleXYFromXY
from editorCode.bufferContainer import BufferContainer
from editorCode.editorTypes import V2

batch = BufferContainer.getInstance()
batch.drawScale = 1.0
drawCircleXYFromXY(batch, 10.0, 10.0, 4.0,3.0, 32, (1,2,3,4))
drawCircle(batch, V2(-20.0, -20.0), V2(1.0,0.0), 32)
for i in range(len(batch.indices)//2):
    i1 = batch.indices[i*2]
    i2 = batch.indices[i*2 + 1]
    print(batch.verts[i1*2:i1*2+2], batch.verts[i2*2:i2*2+2], )


