import numpy as np
import os

def loadObjFile(filename):
    vPos = []
    fin = open(f'{filename}.obj', 'r')
    for line in fin:
        values = line.split() # split by whitespace
        # Skip the row if line is empty or is a comment
        if len(values) == 0 or values[0][0] in ['#', '\0', ' ']:
            continue

        if values[0] == 'v':
            vertices = [float(x) for x in values[1:4]]
            vPos.append(vertices)

    fin.close()
    vPos = np.array(vPos)
    return vPos

def loadXyzFile(filename):
    vPos = []
    fin = open(filename, 'r')
    for line in fin:
        values = line.split() # split by whitespace
        # Skip the row if line is empty or is a comment
        if len(values) == 0 or values[0][0] in ['#', '\0', ' ']:
            continue

        vertices = [float(x) for x in values[0:]]
        vPos.append(vertices)

    fin.close()
    vPos = np.array(vPos)
    return vPos

def saveXyzFile(filename, vertices):
    ofile = open(f"{filename}.xyz", 'w')

    for item in vertices:
        ofile.write(f"{item[0]} {item[1]} {item[2]}\n")

    ofile.close()

def saveObjFile(filename, vertices, faces):
    ofile = open(f"{filename}.obj", 'w')

    for item in vertices:
        ofile.write(f"v {item[0]} {item[1]} {item[2]}\n")

    for face in faces:
        ofile.write(f"f")
        for vert in face:
            ofile.write(f" {vert}")
        ofile.write(f"\n")

    ofile.close()

def updateObjVertices(in_filename, out_filename, vertices):
    os.makedirs(os.path.dirname(out_filename), exist_ok=True)
    fin = open(f'{in_filename}.obj', 'r')
    ofile = open(f"{out_filename}.obj", 'w')

    v = 0
    for line in fin:
        # Remove nul chars from the line
        line = line.rstrip('\x00')
        values = line.split()

        # TODO: Update only vertices values when there are vertex weights (v x y z [w])
        if len(values) > 0 and values[0] == 'v':
            ofile.write(f"v {vertices[v][0]} {vertices[v][1]} {vertices[v][2]}\n")
            v += 1
        else:
            ofile.write(line)
    
    fin.close()
    ofile.close()
    