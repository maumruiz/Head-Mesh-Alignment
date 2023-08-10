from wx import App, Frame, Size, ID_ANY

from interface.layout import Layout
from interface.opengl_canvas import OpenGLCanvas
from core.loader import loadOffFile

DEFAULT_SIZE = Size(1080, 920)

class AlignmentApp(Frame):
     def __init__(self):
          super().__init__(None, ID_ANY, "Head Mesh Alignment", size=DEFAULT_SIZE)
          self.glCanvas = OpenGLCanvas(self)
          self.Centre()
          

          (mesh1VPos, mesh1VColor, mesh1ITris) = loadOffFile('meshes/source.off')
          

          layout = Layout(self, self.glCanvas)
          # layout.bindViewMesh1Button(printSomething)
          
          self.SetSizer(layout.mainSizer)
          self.Layout()

if __name__ == '__main__':
    app = App()
    frame = AlignmentApp()
    frame.Show()
    app.MainLoop()
    app.Destroy()