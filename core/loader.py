import numpy as np
import os

def loadObjFile(filename):
    vPos = []
    vColors = []
    fIdx = []
    fin = open(f'{filename}.obj', 'r')
    for line in fin:
        values = line.split() # split by whitespace
        # Skip the row if line is empty or is a comment
        if len(values) == 0 or values[0][0] in ['#', '\0', ' ']:
            continue

        if values[0] == 'v':
            vertices = [float(x) for x in values[1:]]
            vPos.append(vertices)
            vColors.append([0.9, 0.9, 0.9])

        if values[0] == 'f':
            faceIndices = [int(x.split('/')[0]) for x in values[1:]]
            fIdx.append(faceIndices)

    fin.close()
    vPos = np.array(vPos)
    vColors = np.array(vColors)
    fIdx = np.array(fIdx)

    return vPos, fIdx

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
    fin = open(f'{in_filename}.obj', 'r')
    
    lines1 = []
    lines2 = []
    foundVertices = False

    for line in fin:
        values = line.split()

        if len(values) == 0 or values[0][0] in ['#', '\0', ' ']:
            if foundVertices:
                lines2.append(line)
            else:
                lines1.append(line)
        elif values[0] == 'v':
            foundVertices = True
        else:
            if foundVertices:
                lines2.append(line)
            else:
                lines1.append(line)
    
    fin.close()

    vertices_lines = []
    for item in vertices:
        vertices_lines.append(f"v {item[0]} {item[1]} {item[2]}\n")
    
    final_lines = lines1 + vertices_lines + lines2

    os.makedirs(os.path.dirname(out_filename), exist_ok=True)
    ofile = open(f"{out_filename}.obj", 'w')
    for line in final_lines:
        ofile.write(line)
    ofile.close()