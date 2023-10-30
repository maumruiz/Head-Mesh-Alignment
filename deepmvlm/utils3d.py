import os
import vtk
import numpy as np

class Utils3D:
    def __init__(self, config):
        self.config = config
        self.heatmap_maxima = None
        self.transformations_3d = None
        self.lm_start = None
        self.lm_end = None
        self.landmarks = None

    @staticmethod
    def multi_read_surface(file_name):
        clean_name, file_extension = os.path.splitext(file_name)
        if file_extension == ".obj":
            obj_in = vtk.vtkOBJReader()
            obj_in.SetFileName(file_name)
            obj_in.Update()
            pd = obj_in.GetOutput()
            return pd
        elif file_extension == ".wrl":
            vrmlin = vtk.vtkVRMLImporter()
            vrmlin.SetFileName(file_name)
            vrmlin.Update()
            pd = vrmlin.GetRenderer().GetActors().GetLastActor().GetMapper().GetInput()
            return pd
        elif file_extension == ".vtk":
            pd_in = vtk.vtkPolyDataReader()
            pd_in.SetFileName(file_name)
            pd_in.Update()
            pd = pd_in.GetOutput()
            return pd
        elif file_extension == ".vtp":
            pd_in = vtk.vtkXMLPolyDataReader()
            pd_in.SetFileName(file_name)
            pd_in.Update()
            pd = pd_in.GetOutput()
            return pd
        elif file_extension == ".stl":
            pd_in = vtk.vtkSTLReader()
            pd_in.SetFileName(file_name)
            pd_in.Update()
            pd = pd_in.GetOutput()
            return pd
        elif file_extension == ".ply":
            pd_in = vtk.vtkPLYReader()
            pd_in.SetFileName(file_name)
            pd_in.Update()
            pd = pd_in.GetOutput()
            return pd
        else:
            print("Can not read files with extenstion", file_extension)
            return None
        
    @staticmethod
    def multi_read_texture(file_name, texture_file_name=None):
        if texture_file_name is None:
            img_texture = os.path.splitext(file_name)[0] + ".bmp"
            if os.path.isfile(img_texture):
                texture_file_name = img_texture
            img_texture = os.path.splitext(file_name)[0] + ".png"
            if os.path.isfile(img_texture):
                texture_file_name = img_texture
            img_texture = os.path.splitext(file_name)[0] + ".jpg"
            if os.path.isfile(img_texture):
                texture_file_name = img_texture
            if file_name.find('RAW.wrl') > 0:
                img_texture = file_name.replace('RAW.wrl', 'F3D.bmp')  # BU-3DFE RAW file hack
                if os.path.isfile(img_texture):
                    texture_file_name = img_texture

        # Load texture
        if texture_file_name is not None:
            clean_name, file_extension = os.path.splitext(texture_file_name)
            if file_extension == ".bmp":
                texture_image = vtk.vtkBMPReader()
                texture_image.SetFileName(texture_file_name)
                texture_image.Update()
                return texture_image.GetOutput()
            elif file_extension == ".png":
                texture_image = vtk.vtkPNGReader()
                texture_image.SetFileName(texture_file_name)
                texture_image.Update()
                return texture_image.GetOutput()
            elif file_extension == ".jpg":
                texture_image = vtk.vtkJPEGReader()
                texture_image.SetFileName(texture_file_name)
                texture_image.Update()
                return texture_image.GetOutput()

        return None