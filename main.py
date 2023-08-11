from wx import App, Frame, Size, ID_ANY

from interface.layout import Layout
from interface.opengl_canvas import OpenGLCanvas
from core.loader import loadOffFile

import numpy as np

DEFAULT_SIZE = Size(1080, 920)

class AlignmentApp(Frame):
     def __init__(self):
          super().__init__(None, ID_ANY, "Head Mesh Alignment", size=DEFAULT_SIZE)
          self.Centre()
          
          sourceMesh = loadOffFile('meshes/source.off')
          sourceMesh.performDisplayUpdate()
          
          targetMesh = loadOffFile('meshes/target.off')
          targetMesh.performDisplayUpdate()
          
          self.glCanvas = OpenGLCanvas(self, sourceMesh, targetMesh)
          layout = Layout(self, self.glCanvas)

          layout.bindViewMesh1Button(self.glCanvas.viewSourceMesh)
          layout.bindViewMesh2Button(self.glCanvas.viewTargetMesh)
          layout.bindAlignCentroidsButton(self.glCanvas.centerMeshes)

          self.glCanvas.viewSourceMesh(None)
          
          self.SetSizer(layout.mainSizer)
          self.Layout()
          self.glCanvas.Show()

if __name__ == '__main__':
    app = App()
    frame = AlignmentApp()
    frame.Show()
    app.MainLoop()
    app.Destroy()