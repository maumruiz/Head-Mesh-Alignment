import os
import time
import shutil
import subprocess
from datetime import datetime
from PIL import Image, ImageSequence

from core.loader import loadObjFile, saveXyzFile, updateObjVertices
from core.utils import calculateMaxEucDist, getCentroid
from deepmvlm.api import DeepMVLM
from deepmvlm.parse_config import ConfigParser

CONFIG_FILE = 'RGB+depth.json'

class Processor:
    def __init__(self, target_filename, base_file):
        self.target_filename = target_filename
        self.base_file = 'assets/base'
        self.timestamp = datetime.now().strftime(r'%y%m%d_%H%M%S')
        config = ConfigParser(f'deepmvlm/configs/{CONFIG_FILE}', self.timestamp, target_filename)
        self.config = config

        print('-- Preprocessing')
        # Copy files to tmp directory
        filepath = f'input/{target_filename}'
        if os.path.exists(f'{filepath}.obj'):
            shutil.copy(f'{filepath}.obj', str(config.save_dir / f'{target_filename}.obj'))
        
        if os.path.exists(f'{filepath}.mtl'):
            shutil.copy(f'{filepath}.mtl', str(config.save_dir / f'{target_filename}.mtl'))

        if os.path.exists(f'{filepath}.png'):
            shutil.copy(f'{filepath}.png', str(config.save_dir / f'{target_filename}.png'))
        elif os.path.exists(f'{filepath}.jpg'):
            shutil.copy(f'{filepath}.jpg', str(config.save_dir / f'{target_filename}.jpg'))
        elif os.path.exists(f'{filepath}.tif'):
            im = Image.open(f'{filepath}.tif')
            im = im.convert('RGB')
            for i, page in enumerate(ImageSequence.Iterator(im)):
                page.save(str(config.save_dir / f'{target_filename}.jpg'))
            fin = open(str(config.save_dir / f'{target_filename}.mtl'), 'r')
            ofile = open(str(config.save_dir / f'{target_filename}.mtl.tmp'), 'w')
            for line in fin:
                if 'tif' in line:
                    idx = line.index('tif')
                    ofile.write(line[:idx] + 'jpg')
                else:
                    ofile.write(line)
            ofile.write('')
            fin.close()
            ofile.close()
            os.remove(str(config.save_dir / f'{target_filename}.mtl'))
            os.rename(str(config.save_dir / f'{target_filename}.mtl.tmp'), str(config.save_dir / f'{target_filename}.mtl'))

        self.dm = DeepMVLM(config)

    def align(self):
        in_filename = str(self.config.save_dir / f'{self.target_filename}')
        out_filename = f'output/{self.target_filename}_aligned.obj'

        start = time.time()

        aligned_filename = f'tmp/{self.timestamp}/{self.target_filename}_prealigned'
        self.preAlignMesh(in_filename, aligned_filename)

        for i in range(1, 3):
            print(f'##### Iteration {i} #####')
            landmarksFilename = f'tmp/{self.timestamp}/{self.target_filename}_landmarks_{i}'
            self.detectLandmarks(f'{aligned_filename}.obj', landmarksFilename)
            out_aligned_file = f'tmp/{self.timestamp}/{self.target_filename}_aligned_{i}'
            self.scaleICP(landmarksFilename, aligned_filename, out_aligned_file)
            aligned_filename = out_aligned_file

        end = time.time()

        shutil.copy(f'{aligned_filename}.obj', out_filename)
        print(f'----- Execution time: {(end-start) / 60} minutes')
        print(f"----- Result saved in {out_filename}")

    def preAlignMesh(self, in_filename, out_filename):
        print('--- Prealigning mesh...')

        t_vertices = loadObjFile(in_filename)
        targetCentroid = getCentroid(t_vertices)
        target_vertices = t_vertices - targetCentroid.T
        base_vertices = loadObjFile(f'{self.base_file}')

        target_maxDist = calculateMaxEucDist(target_vertices)
        base_maxDist = calculateMaxEucDist(base_vertices)

        euc_ratio = base_maxDist / target_maxDist
        scaled_vertices = target_vertices * euc_ratio

        print(f'Scale ratio: {euc_ratio}')

        updateObjVertices(in_filename, out_filename, scaled_vertices)

    def detectLandmarks(self, in_filename, out_filename):
        print('--- Detecting landmarks...')
        landmarks = self.dm.predict(in_filename, out_filename)
        saveXyzFile(out_filename, landmarks)

        return out_filename

    def scaleICP(self, landmarks, in_file, out_filename):
        print("---Aligning with ICP...")
        base_landmarks = f'assets/base_landmarks'
        subprocess.run(["./scaleICP/scaleICP.exe", landmarks, base_landmarks, in_file, out_filename])