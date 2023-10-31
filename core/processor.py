from datetime import datetime
import subprocess
import shutil

from core.loader import loadObjFile, saveXyzFile, updateObjVertices
from core.utils import calculateMaxEucDist, getCentroid
from deepmvlm.api import DeepMVLM
from deepmvlm.parse_config import ConfigParser

CONFIG_FILE = 'geometry+depth.json'

class Processor:
    def __init__(self, target_filename, base_file):
        self.target_filename = target_filename
        self.base_file = 'assets/base'
        self.timestamp = datetime.now().strftime(r'%y%m%d_%H%M%S')

    def align(self):
        out_filename = f'output/{self.target_filename}_aligned.obj'

        prealignedFilename = self.preAlignMesh()
        landmarksFilename = self.detectLandmarks(f'{prealignedFilename}.obj')
        alignedFilename = self.scaleICP(landmarksFilename, prealignedFilename, self.target_filename)
        shutil.copy(f'{alignedFilename}.obj', out_filename)
        print(f"-----Result saved in {out_filename}")

    def preAlignMesh(self):
        print('--- Prealigning mesh...')
        in_filename = f'input/{self.target_filename}'
        out_filename = f'tmp/{self.timestamp}/{self.target_filename}_prealigned'

        t_vertices, _ = loadObjFile(in_filename)
        targetCentroid = getCentroid(t_vertices)
        target_vertices = t_vertices - targetCentroid.T
        base_vertices, _ = loadObjFile(f'{self.base_file}')

        target_maxDist = calculateMaxEucDist(target_vertices)
        base_maxDist = calculateMaxEucDist(base_vertices)

        euc_ratio = base_maxDist / target_maxDist
        scaled_vertices = target_vertices * euc_ratio

        print(f'Scale ratio: {euc_ratio}')

        updateObjVertices(in_filename, out_filename, scaled_vertices)
        return out_filename

    def detectLandmarks(self, in_filename):
        print('--- Detecting landmarks...')
        out_filename = f'tmp/{self.timestamp}/{self.target_filename}_landmarks'
        
        config = ConfigParser(f'deepmvlm/configs/{CONFIG_FILE}', self.timestamp)
        dm = DeepMVLM(config)
        landmarks = dm.predict(in_filename)
        saveXyzFile(out_filename, landmarks)

        return out_filename

    def scaleICP(self, landmarks, in_file, mesh_name):
        print("---Aligning with ICP...")
        base_landmarks = f'assets/base_landmarks'
        out_filename = f'tmp/{self.timestamp}/{mesh_name}_aligned'
        subprocess.run(["./scaleICP/scaleICP.exe", landmarks, base_landmarks, in_file, out_filename])
        return out_filename