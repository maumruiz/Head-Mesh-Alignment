from OpenGL.GL import *
from wx import glcanvas, PaintDC
from wx import EVT_ERASE_BACKGROUND, EVT_PAINT

class OpenGLCanvas(glcanvas.GLCanvas):
     def __init__(self, parent):
          attribs = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24)
          super().__init__(parent, -1, attribList = attribs)
          self.context = glcanvas.GLContext(self)

          self.GLinitialized = False
          #GL-related events
          self.Bind(EVT_ERASE_BACKGROUND, self.OnEraseBackground)
          # EVT_SIZE(self, self.processSizeEvent)
          self.Bind(EVT_PAINT, self.OnPaint)

     def OnEraseBackground(self, event):
          pass # Do nothing, to avoid flashing on MSW.
     
     def OnPaint(self, event):
          dc = PaintDC(self)
          self.SetCurrent(self.context)
          if not self.GLinitialized:
               self.initGL()
               self.GLinitialized = True
          self.OnDraw()

     def OnDraw(self):
          # Set clear color
          glClearColor(0.15, 0.15, 0.15, 1.0)
          #Clear the screen to black
          glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
          self.SwapBuffers()
     
     def initGL(self):        
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glEnable(GL_LIGHT1)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)