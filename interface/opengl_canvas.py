import numpy as np
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from wx import glcanvas, PaintDC
from wx import EVT_ERASE_BACKGROUND, EVT_PAINT
import wx

from core.camera import MousePolarCamera
from core.data_structures import BBox3D
from core.icp import getCentroid, getCorrespondences, getProcrustesAlignment, execICP

class OpenGLCanvas(glcanvas.GLCanvas):
     def __init__(self, parent, sourceMesh, targetMesh):
          self.sourceMesh = sourceMesh
          self.targetMesh = targetMesh
          attribs = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24)
          super().__init__(parent, -1, attribList = attribs)
          self.context = glcanvas.GLContext(self)
          self.size = self.GetClientSize()
          self.camera = MousePolarCamera(self.size.width, self.size.height)
          self.MousePos = [0, 0]

          self.nearDist = 0.01
          self.farDist = 1000.0

          #######################
          # CALCULATED
          #######################
          self.currSc = np.array([[0, 0, 0]]).T #Current Source Centroid
          self.currTc = np.array([[0, 0, 0]]).T #Current Target Centroid
          self.currRx = np.eye(3) #Current rotation
          self.corresIdx = np.zeros([]) #Current correspondences indexes
          self.corresBuffer = None #Correspondence vertex buffer
          self.ScUpdates = []
          self.TcUpdates = []
          self.RxUpdates = []
          #########################

          self.GLinitialized = False
          #GL events
          self.Bind(EVT_ERASE_BACKGROUND, self.OnEraseBackground)
          # EVT_SIZE(self, self.processSizeEvent)
          self.Bind(EVT_PAINT, self.OnPaint)

          # Mouse events
          #Mouse Events
          self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
          self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
          self.Bind(wx.EVT_RIGHT_DOWN, self.MouseDown)
          self.Bind(wx.EVT_RIGHT_UP, self.MouseUp)
          self.Bind(wx.EVT_MIDDLE_DOWN, self.MouseDown)
          self.Bind(wx.EVT_MIDDLE_UP, self.MouseUp)
          self.Bind(wx.EVT_MOTION, self.MouseMotion)

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
          self.setupPerspectiveMatrix(self.nearDist, self.farDist)
          # Set clear color
          glClearColor(0.15, 0.15, 0.15, 1.0)
          #Clear the screen to black
          glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
          
          # Add lightning
          glEnable(GL_LIGHTING)
          glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
          glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
          glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 64)

          # Position camera
          self.camera.gotoCameraFrame()
          P = np.zeros(4)
          P[0:3] = self.camera.eye   
          glLightfv(GL_LIGHT0, GL_POSITION, P)

          # Render meshes
          self.renderMesh(self.sourceMesh, self.currSc, "red")
          self.renderMesh(self.targetMesh, self.currTc, "blue")

          if self.corresBuffer:
               self.drawLines(self.corresBuffer, self.sourceMesh.VPos.shape[0])

          self.SwapBuffers()

     def getBBoxs(self):
          #Make Source bounding box
          Vsource = self.sourceMesh.VPos.T - self.currSc
          sourceBbox = BBox3D(Vsource.T)
          
          #Make target bounding box
          Vtarget = self.targetMesh.VPos.T - self.currTc
          Vtarget = self.currRx.dot(Vtarget)
          targetBbox = BBox3D(Vtarget.T)
          
          bboxall = BBox3D(np.concatenate((Vsource, Vtarget), 1).T)
          self.farDist = bboxall.getDiagLength()*20
          self.nearDist = self.farDist/10000.0
          return (sourceBbox, targetBbox)

     def viewSourceMesh(self, event):
          (bbox, _) = self.getBBoxs()
          self.camera.centerOnBBox(bbox)
          self.Refresh()
     
     def viewTargetMesh(self, event):
          (_, bbox) = self.getBBoxs()
          self.camera.centerOnBBox(bbox)
          self.Refresh()

     def renderMesh(self, mesh, centroid, color):
          TC = np.eye(4)
          TC[0:3, 3] = -centroid.flatten()
          glPushMatrix()
          glMultMatrixd((TC.T).flatten())

          if mesh.needsDisplayUpdate:
               mesh.performDisplayUpdate()
               mesh.needsDisplayUpdate = False
          
          glEnable(GL_LIGHTING)
          self.drawFaces(mesh)
          if color == "red":
               glColor3f(1.0, 0, 0)
          else:
               glColor3f(0, 0, 1.0)
          self.drawPoints(mesh)
          glPopMatrix()
     
     def drawPoints(self, mesh):
          glEnableClientState(GL_VERTEX_ARRAY)
          mesh.VPosVBO.bind()
          glVertexPointerf(mesh.VPosVBO)
          glDisable(GL_LIGHTING)
          glPointSize(3)
          glDrawArrays(GL_POINTS, 0, mesh.VPos.shape[0])
          mesh.VPosVBO.unbind()
          glDisableClientState(GL_VERTEX_ARRAY)
     
     def drawFaces(self, mesh):
          glEnableClientState(GL_VERTEX_ARRAY)
          glEnableClientState(GL_COLOR_ARRAY)
          glEnableClientState(GL_NORMAL_ARRAY)
          mesh.VPosVBO.bind()
          glVertexPointerf(mesh.VPosVBO)
          mesh.VNormalsVBO.bind()
          glNormalPointerf(mesh.VNormalsVBO)
          mesh.VColorsVBO.bind()
          glColorPointerf(mesh.VColorsVBO)
          
          # Dont use texture
          glEnable(GL_COLOR_MATERIAL)
          glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

          mesh.IndexVBO.bind()
          glDrawElements(GL_QUADS, 4*mesh.ITris.shape[0], GL_UNSIGNED_INT, None)
          mesh.IndexVBO.unbind()

          mesh.VPosVBO.unbind()
          mesh.VNormalsVBO.unbind()
          mesh.VColorsVBO.unbind()
          glDisableClientState(GL_NORMAL_ARRAY)
          glDisableClientState(GL_COLOR_ARRAY)
          glDisableClientState(GL_VERTEX_ARRAY)
     
     def drawLines(self, buff, nLines):
          glColor3f(0, 1.0, 0)
          glEnableClientState(GL_VERTEX_ARRAY)
          buff.bind()
          glVertexPointerf(buff)
          glDisable(GL_LIGHTING)
          glPointSize(7)
          glDrawArrays(GL_LINES, 0, nLines*2)
          buff.unbind()
          glDisableClientState(GL_VERTEX_ARRAY)
     
     def centerMeshes(self, event):
          self.currSc = getCentroid(self.sourceMesh.VPos.T)
          self.currTc = getCentroid(self.targetMesh.VPos.T)

          if self.corresBuffer:
               self.updateCorrBuffer()

          self.viewSourceMesh(None)
          print(f"Centroids: {self.currSc} and {self.currTc}")
     
     def findCorrespondences(self, event):
          print('Calculating correspondences...')
          X = self.sourceMesh.VPos.T
          Y = self.targetMesh.VPos.T
          self.corresIdx = getCorrespondences(X, Y, self.currSc, self.currTc, self.currRx)
          self.updateCorrBuffer()
          self.Refresh()
          print(f"Correspondences: {self.corresIdx} with shape: {self.corresIdx.shape}")
     
     def computeProcrustes(self, event):
        if not self.corresBuffer:
            wx.MessageBox('Must compute correspondences before doing procrustes!', 'Error', wx.OK | wx.ICON_ERROR)
            return
        
        print("Computing Procrustes...")
        X = self.sourceMesh.VPos.T
        Y = self.targetMesh.VPos.T
        (self.currCx, self.currCy, self.currRx) = getProcrustesAlignment(X, Y, self.corresIdx)
        self.updateCorrBuffer()
        self.Refresh()
        print(f"Cx: {self.currCx} - Cy: {self.currCy} - Rx: {self.currRx}")

     def computeICP(self, event):
          print("Computing ICP...")
          (self.currRx, self.currSc) = execICP(self.sourceMesh.VPos, self.targetMesh.VPos)
          self.corridxbuff = None
          self.viewSourceMesh(None)
          self.Refresh()
     
     def updateCorrBuffer(self):
          # Translate vertex buffers to the center
          X = self.sourceMesh.VPos.T - self.currSc
          Y = self.targetMesh.VPos.T - self.currTc
          # Apply rotation to the source mesh
          X = self.currRx.dot(X)
          # Create the correspondence buffer
          N = self.corresIdx.size
          C = np.zeros((N*2, 3))
          # Fill the correspondence buffer
          C[0::2, :] = X.T
          C[1::2, :] = Y.T[self.corresIdx, :]
          # Create VBO with the data
          self.corresBuffer = vbo.VBO(np.array(C, dtype=np.float32))
     
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
     
     def setupPerspectiveMatrix(self, nearDist = -1, farDist = -1):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if nearDist == -1:
            farDist = self.camera.eye - self.bbox.getCenter()
            farDist = np.sqrt(farDist.dot(farDist)) + self.bbox.getDiagLength()
            nearDist = farDist/50.0
        gluPerspective(180.0*self.camera.yfov/math.pi, float(self.size.x)/self.size.y, nearDist, farDist)

     def handleMouseStuff(self, x, y):
        #Invert y from what the window manager says
        y = self.size.height - y
        self.MousePos = [x, y]

     def MouseDown(self, evt):
          state = wx.GetMouseState()
          x, y = evt.GetPosition()
          self.CaptureMouse()
          self.handleMouseStuff(x, y)
          self.Refresh()
     
     def MouseUp(self, evt):
          x, y = evt.GetPosition()
          self.handleMouseStuff(x, y)
          self.ReleaseMouse()
          self.Refresh()

     def MouseMotion(self, evt):
          state = wx.GetMouseState()
          x, y = evt.GetPosition()
          [lastX, lastY] = self.MousePos
          self.handleMouseStuff(x, y)
          dX = self.MousePos[0] - lastX
          dY = self.MousePos[1] - lastY
          if evt.Dragging():
               #Translate/rotate shape
               if evt.MiddleIsDown():
                    self.camera.translate(dX, dY)
               elif evt.RightIsDown():
                    self.camera.zoom(-dY)#Want to zoom in as the mouse goes up
               elif evt.LeftIsDown():
                    self.camera.orbitLeftRight(dX)
                    self.camera.orbitUpDown(dY)
          self.Refresh() 