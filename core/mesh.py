import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *

from core.data_structures import BBox3D

class Mesh():
    def __init__(self, VPos=None, VColors=None, ITris=None):
        # Arrays with geometric information
        if VPos is None:
            self.VPos = np.zeros((0, 3)) # Vertex buffer (np.float32)
        else:
            self.VPos = VPos

        if VColors is None:
            self.VColors = np.zeros((0, 3)) # Color buffer (np.float32)
        else:
            self.VColors = VColors

        if ITris is None:
            self.ITris = np.zeros((0, 3)) # Triangle index buffer (np.float32)
        else:
            self.ITris = ITris
        
        self.EdgeLines = np.zeros((0, 3)) # Edge lines
        self.VNormals = np.zeros((0, 3)) # Vertex Normals

        #Buffer pointers
        self.VPosVBO = None
        self.VColorsVBO = None
        self.IndexVBO = None
        self.VNormalsVBO = None
        self.EdgeLinesVBO = None
        self.VNormalLinesVBO = None
        self.FNormalLinesVBO = None

    def getBBox(self):
        if self.VPos.shape[0] == 0:
            print("Warning: Mesh.getBBox(): Adding bbox but no vertices")
            return BBox3D()
        bbox = BBox3D(self.VPos)
        return bbox
    
    # Update normal vectors
    def updateNormalBuffer(self):
        # Compute the cross product of vectors representing the edges of each triangle
        # The cross product of two edge vectors gives the normal vector of the corresponding face
        V1 = self.VPos[self.ITris[:, 1], :] - self.VPos[self.ITris[:, 0], :]
        V2 = self.VPos[self.ITris[:, 2], :] - self.VPos[self.ITris[:, 0], :]
        FNormals = np.cross(V1, V2)

        # Compute the area of each face using the euclidean norm
        FAreas = np.reshape(np.sqrt(np.sum(FNormals**2, 1)), (FNormals.shape[0], 1))
        FAreas[FAreas == 0] = 1 # If area 0, set it to 1 to avoid division by 0

        # Normalize the face normal vectors
        FNormals = FNormals/FAreas

        # Initialize FNormals, FCentroid and VNormals with zero arrays
        self.FNormals = FNormals
        self.FCentroid = 0*FNormals
        self.VNormals = 0*self.VPos
        VAreas = np.zeros((self.VPos.shape[0], 1))

        # Calculate vertex normals by summing up the normalized face normals of the adjacent
        # faces that share a vertex.
        for k in range(4):
            self.VNormals[self.ITris[:, k], :] += FAreas*FNormals
            VAreas[self.ITris[:, k]] += FAreas # Accumulate the areas of the adjacent faces
            self.FCentroid += self.VPos[self.ITris[:, k], :] # Calculate centroid of each face
        self.FCentroid /= 4

        # Normalize vertex normals by dividing each vector by its corresponding accumulated
        # vertex area
        VAreas[VAreas == 0] = 1
        self.VNormals = self.VNormals / VAreas


    # Right now this works for buffers only, where there is no mesh structure
    #  other than VPos, VColors, ITris
    def performDisplayUpdate(self):
        # Clear buffers
        if self.VPosVBO:
            self.VPosVBO.delete()
        if self.VNormalsVBO:
            self.VNormalsVBO.delete()
        if self.VColorsVBO:
            self.VColorsVBO.delete()
        if self.IndexVBO:
            self.IndexVBO.delete()
        if self.EdgeLinesVBO:
            self.EdgeLinesVBO.delete()
        if self.VNormalLinesVBO:
            self.VNormalLinesVBO.delete()
        if self.FNormalLinesVBO:
            self.FNormalLinesVBO.delete()

        self.VPosVBO = vbo.VBO(np.array(self.VPos, dtype=np.float32))
        self.VColorsVBO = vbo.VBO(np.array(self.VColors, dtype=np.float32))
        self.IndexVBO = vbo.VBO(self.ITris, target=GL_ELEMENT_ARRAY_BUFFER)

        #Use triangle faces to add edges (will be redundancy but is faster
            #tradeoff for rendering only)
        NTris = self.ITris.shape[0]
        self.EdgeLines = np.zeros((NTris*4*2, 3))
        for k in range(4):
            istart = k*NTris*2
            self.EdgeLines[istart:istart+NTris*2:2, :] = self.VPos[self.ITris[:, k], :]
            self.EdgeLines[istart+1:istart+NTris*2:2, :] = self.VPos[self.ITris[:, (k+1)%4], :]
        self.EdgeLinesVBO = vbo.VBO(np.array(self.EdgeLines, dtype=np.float32))
        
        #Update face and vertex normals
        scale = 1 * self.getBBox().getDiagLength()
        self.updateNormalBuffer()
        self.VNormalsVBO = vbo.VBO(np.array(self.VNormals, dtype=np.float32))

        # Create vertex normal visualization lines
        VNList = np.zeros((self.VPos.shape[0]*2, 3)) # Double rows for the orig vertex pos and displaced
        VNList[np.arange(0, VNList.shape[0], 2), :] = self.VPos # Assign original positions
        VNList[np.arange(1, VNList.shape[0], 2), :] = self.VPos + scale*self.VNormals # Assign displaced position
        self.VNormalLinesVBO = vbo.VBO(np.array(VNList, dtype=np.float32))

        # Create face normals visualization lines
        VFList = np.zeros((self.ITris.shape[0]*2, 3))
        VFList[np.arange(0, VFList.shape[0], 2), :] = self.FCentroid
        VFList[np.arange(1, VFList.shape[0], 2), :] = self.FCentroid + scale*self.FNormals
        self.FNormalLinesVBO = vbo.VBO(np.array(VFList, dtype=np.float32))
        
        self.needsDisplayUpdate = False