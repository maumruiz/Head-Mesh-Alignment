import wx
from wx import App, Frame, Size, Point, ID_ANY, glcanvas, PaintDC, BoxSizer
from wx import EVT_ERASE_BACKGROUND, EVT_SIZE, EVT_PAINT

class Layout():
    def __init__(self, parent, glCanvas):
        self.parent = parent
        toolBar = BoxSizer(wx.HORIZONTAL)
        self.viewMesh1Button = wx.Button(parent, -1, "View Source")
        toolBar.Add(self.viewMesh1Button, 0, wx.EXPAND)
        self.viewMesh2Button = wx.Button(parent, -1, "View Target")
        toolBar.Add(self.viewMesh2Button, 0, wx.EXPAND)

        self.alignCentroidsButton = wx.Button(parent, -1, "Align Centroids")
        toolBar.Add(self.alignCentroidsButton, 0, wx.EXPAND)
        self.findCorrespondencesButton = wx.Button(parent, -1, "Find Correspondences")
        toolBar.Add(self.findCorrespondencesButton, 0, wx.EXPAND)

        self.mainSizer = BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(glCanvas, 2, wx.EXPAND)
        self.mainSizer.Add(toolBar, 0, wx.EXPAND)

    def bindViewMesh1Button(self, func):
        self.parent.Bind(wx.EVT_BUTTON, func, self.viewMesh1Button)
    
    def bindViewMesh2Button(self, func):
        self.parent.Bind(wx.EVT_BUTTON, func, self.viewMesh2Button)
    
    def bindAlignCentroidsButton(self, func):
        self.parent.Bind(wx.EVT_BUTTON, func, self.alignCentroidsButton)

    def bindFindCorrespondencesButton(self, func):
        self.parent.Bind(wx.EVT_BUTTON, func, self.findCorrespondencesButton)