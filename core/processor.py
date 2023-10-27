from datetime import datetime
import open3d as o3d
import numpy as np
from core.loader import loadObjFile, saveXyzFile, updateObjVertices
from core.utils import calculateMaxEucDist, getCentroid

class Processor:
    def __init__(self, target_filename, base_filename):
        self.target_filename = target_filename
        self.base_filename = base_filename
        self.timestamp = datetime.now().strftime(r'%y%m%d_%H%M%S')
        print(self.timestamp)

    def align(self):
        prealignedFilename = self.preAlignMesh()
        landmarksFilename = self.detectLandmarks(prealignedFilename)

    def preAlignMesh(self):
        print('Prealigning mesh...')
        in_filename = f'input/{self.target_filename}'
        out_filename = f'tmp/{self.timestamp}/{self.target_filename}_prealigned'

        t_vertices, _ = loadObjFile(in_filename)
        targetCentroid = getCentroid(t_vertices)
        target_vertices = t_vertices - targetCentroid.T
        base_vertices, _ = loadObjFile(f'input/{self.base_filename}')

        target_maxDist = calculateMaxEucDist(target_vertices)
        base_maxDist = calculateMaxEucDist(base_vertices)

        euc_ratio = base_maxDist / target_maxDist
        scaled_vertices = target_vertices * euc_ratio

        print(f'Scale ratio: {euc_ratio}')

        updateObjVertices(in_filename, out_filename, scaled_vertices)
        return out_filename

    def detectLandmarks(self, filename):
        print('Detecting landmarks...')
        out_filename = f'tmp/{self.timestamp}/{self.target_filename}_landmarks'

        

        return out_filename

    def scaleICP(self):
        pass