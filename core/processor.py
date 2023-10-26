import open3d as o3d
import numpy as np
from core.loader import loadObjFile, saveXyzFile

TARGET_SAMPLE_NUM = 12000

def downsampleMesh(name):
    print('Downsampling Scan... ')
    vertices, faces = loadObjFile(f'input/{name}.obj')
    
    sample_by = 2
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(vertices)
    downsampled = np.asarray(pcd.uniform_down_sample(sample_by).points)
    
    while downsampled.shape[0] > TARGET_SAMPLE_NUM:
        sample_by += 1
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(vertices)
        downsampled = np.asarray(pcd.uniform_down_sample(sample_by).points)

    print(f'Sampled by: {sample_by}')
    print(f'Shape: {downsampled.shape}')

    saveXyzFile(f'tmp/{name}_downsampled', downsampled)

def scaleICP():
    pass