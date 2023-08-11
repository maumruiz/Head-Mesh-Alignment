import math
import numpy as np
from OpenGL.GL import *

from core.data_structures import BBox3D

class MousePolarCamera(object):
    #Coordinate system is defined as in OpenGL as a right
    #handed system with +z out of the screen, +x to the right,
    #and +y up
    #phi is CCW down from +y, theta is CCW away from +z
    def __init__(self, pixWidth, pixHeight, yfov = 0.75):
        self.pixWidth = pixWidth
        self.pixHeight = pixHeight
        self.yfov = yfov
        self.nearDist = 0.1
        self.farDist = 10.0
        self.center = np.array([0, 0, 0])
        self.R = 1
        self.theta = 0
        self.phi = 0 
        self.updateVecsFromPolar()
    
    def setNearFar(self, nearDist, farDist):
        self.nearDist = nearDist
        self.farDist = farDist
    
    def centerOnBBox(self, bbox, theta = -math.pi/2, phi = math.pi/2):
        self.center = bbox.getCenter()
        self.R = bbox.getDiagLength()*1.5
        self.theta = theta
        self.phi = phi
        self.updateVecsFromPolar()        

    def centerOnPoints(self, X):
        bbox = BBox3D()
        bbox.fromPoints(X)
        self.centerOnBBox(bbox)

    def updateVecsFromPolar(self):
        [sinT, cosT, sinP, cosP] = [math.sin(self.theta), math.cos(self.theta), math.sin(self.phi), math.cos(self.phi)]
        #Make the camera look inwards
        #i.e. towards is -dP(R, phi, theta)/dR, where P(R, phi, theta) is polar position
        self.towards = np.array([-sinP*cosT, -cosP, sinP*sinT])
        self.up = np.array([-cosP*cosT, sinP, cosP*sinT])
        self.eye = self.center - self.R*self.towards

    #This function pushes a matrix onto the stack that puts everything
    #in the frame of a camera which is centered at position "P",
    #is pointing towards "t", and has vector "r" to the right
    #towards - towards vector
    #up      - up vector
    #r       - right vector
    #eye     - Camera center
    def gotoCameraFrame(self):
        matFlatten = self.getModelviewMatrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixd(matFlatten)
    
    def getModelviewMatrix(self):
        r = np.cross(self.towards, self.up)
        rotMat = np.array([ [r[0], self.up[0], -self.towards[0], 0], [r[1], self.up[1], -self.towards[1], 0], [r[2], self.up[2], -self.towards[2], 0], [0, 0, 0, 1] ])
        rotMat = rotMat.T
        transMat = np.array([ [1, 0, 0, -self.eye[0]], [0, 1, 0, -self.eye[1]], [0, 0, 1, -self.eye[2]], [0, 0, 0, 1] ])
        #Translate first then rotate
        mat = rotMat.dot(transMat)
        #OpenGL is column major and mine are row major so take transpose
        mat = mat.T
        return mat.flatten()
    
    def getPerspectiveMatrix(self, yfov, aspect, near, far):
        f = 1.0/math.tan(yfov/2)
        nf = 1/(near - far)
        mat = np.zeros(16)
        mat[0] = f/aspect
        mat[5] = f
        mat[10] = (far + near)*nf
        mat[11] = -1
        mat[14] = (2*far*near)*nf
        return mat
    
    def orbitUpDown(self, dP):
        dP = 1.5*dP/float(self.pixHeight)
        self.phi = self.phi+dP
        self.updateVecsFromPolar()
    
    def orbitLeftRight(self, dT):
        dT = 1.5*dT/float(self.pixWidth)
        self.theta = self.theta-dT
        self.updateVecsFromPolar()
    
    def zoom(self, rate):
        rate = rate / float(self.pixHeight)
        self.R = self.R*pow(4, rate)
        self.updateVecsFromPolar()
    
    def translate(self, dx, dy):
        length = self.center - self.eye
        length = np.sqrt(np.sum(length**2))*math.tan(self.yfov)
        dx = length*dx / float(self.pixWidth)
        dy = length*dy / float(self.pixHeight)
        r = np.cross(self.towards, self.up)
        self.center = self.center - dx*r - dy*self.up
        self.eye = self.eye - dx*r - dy*self.up
        self.updateVecsFromPolar()