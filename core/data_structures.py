import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *

class BBox3D(object):
    def __init__(self, points=None):
        self.box = np.array([[np.inf, np.inf, np.inf], [-np.inf, -np.inf, -np.inf]])
        if points is not None:
            self.box[0, :] = np.min(points, 0)
            self.box[1, :] = np.max(points, 0)
    
    def getDiagLength(self):
        dB = self.box[1, :] - self.box[0, :]
        return np.sqrt(dB.dot(dB))
    
    def getCenter(self):
        return np.mean(self.box, 0)
    
    def addPoint(self, point):
        self.box[0, :] = np.min((point, self.box[0, :]), 0)
        self.box[1, :] = np.max((point, self.box[1, :]), 0)
    
    def Union(self, other):
        self.box[0, :] = np.min(self.box[0, :], other.b[0, :])
        self.box[1, :] = np.max(self.box[1, :], other.b[1, :])
    
    def __str__(self):
        coords = self.box.T.flatten()
        ranges = (self.box[1, :] - self.box[0, :]).flatten()
        return "BBox3D: [%g, %g] x [%g, %g] x [%g, %g],  Range (%g x %g x %g)"%tuple(coords.tolist() + ranges.tolist())