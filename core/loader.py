import numpy as np
from core.mesh import Mesh

# Load files with .off extension
def loadOffFile(filename):
    fin = open(filename, 'r')
    nVertices = 0
    nFaces = 0
    currVertex = 0
    currFace = 0

    VPos = np.zeros((0, 3)) # Vertex buffer
    VColors = np.zeros((0, 3)) # Color buffer
    ITris = np.zeros((0, 3)) # Triangle index buffer

    for line in fin:
        values = line.split() # split by whitespace
        # Skip the row if line is empty or is a comment
        if len(values) == 0 or values[0][0] in ['#', '\0', ' '] or len(values[0]) == 0:
            continue
        
        if nVertices == 0:
            if values[0] == "OFF":
                continue
            else:
                nVertices, nFaces, nEdges = [int(value) for value in values]
                print(f"Number of Vertices: {nVertices} -- Number of Faces: {nFaces}")
                VPos = np.zeros((nVertices, 3))
                VColors = np.zeros((nVertices, 3))
                ITris = np.zeros((nFaces, 3))
        elif currVertex < nVertices:
            values = [float(value) for value in values]
            VPos[currVertex, :] = [values[0], values[1], values[2]]
            VColors[currVertex, :] = np.array([0.9, 0.9, 0.9]) # Grey by default
            currVertex += 1
        elif currFace < nFaces:
            values = [int(value) for value in values]
            ITris[currFace, :] = values[1: values[0]+1]
            currFace += 1

    fin.close()
    VPos = np.array(VPos, np.float64)
    VColors = np.array(VColors, np.float64)
    ITris = np.array(ITris, np.int32)

    return Mesh(VPos, VColors, ITris)