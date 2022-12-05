import cv2
import wx
import math
import numpy as np


class MainFrame(wx.Frame):
    def __init__(self, title):
        super().__init__(None, title=title)
        # Считает количество подключенных камер
        self.camName = []
        max_tested = 100
        for i in range(max_tested):
            temp_camera = cv2.VideoCapture(i)
            if temp_camera.isOpened():
                temp_camera.release()
                self.camName.append("Камера №" + str(i))
                continue
            break

        # Window settings
        self.SetBackgroundColour(wx.Colour(0, 170, 200))
        self.Maximize(True)
        #
        self.W, self.H = self.GetSize()
        panel = wx.Panel(self)

        # Menu
        fileMenu = wx.Menu()
        self.exitItem = wx.MenuItem(fileMenu, wx.ID_ANY, text="Выход\tCtrl+Q")
        fileMenu.Append(self.exitItem)
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "Файл")
        self.SetMenuBar(menuBar)
        #

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.grayBox = wx.CheckBox(panel, label="Gray")
        hbox.Add(self.grayBox, proportion=1, flag=wx.LEFT | wx.UP, border=2)
        self.redBox = wx.CheckBox(panel, label="Red")
        hbox.Add(self.redBox, proportion=1, flag=wx.UP, border=2)
        self.greenBox = wx.CheckBox(panel, label="Green")
        hbox.Add(self.greenBox, proportion=1, flag=wx.UP, border=2)
        self.blueBox = wx.CheckBox(panel, label="Blue")
        hbox.Add(self.blueBox, proportion=1, flag=wx.UP, border=2)

        self.cameraSelection = wx.ComboBox(panel, pos=(
            50, 30), choices=self.camName, style=wx.CB_READONLY)
        self.cameraSelection.SetSelection(0)
        hbox.Add(self.cameraSelection, proportion=1,
                 flag=wx.UP, border=2)

        self.acceptBtn = wx.Button(panel, label="Принять")
        hbox.Add(self.acceptBtn, proportion=1, flag=wx.UP | wx.RIGHT, border=2)

        vbox.Add(hbox, flag=wx.EXPAND | wx.DOWN, border=2)

        # Панель с камерой
        self.VideoFrame = VideoFrame(
            panel, int(self.W), int(self.H))

        vbox.Add(self.VideoFrame)
        panel.SetSizer(vbox)

        self.acceptBtn.Bind(wx.EVT_BUTTON, self.AcceptVideoMode)
        self.Bind(wx.EVT_MENU, self.OnExit, self.exitItem)
        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)
        self.Show()

    def AcceptVideoMode(self, event):
        if self.grayBox.GetValue():
            self.VideoFrame.VideoMode = "gray"
        elif self.redBox.GetValue():
            self.VideoFrame.VideoMode = "red"
        elif self.greenBox.GetValue():
            self.VideoFrame.VideoMode = "green"
        elif self.blueBox.GetValue():
            self.VideoFrame.VideoMode = "blue"
        else:
            self.VideoFrame.VideoMode = "default"

        self.VideoFrame.CamNumber = str.split(
            self.cameraSelection.Value, '№')[1]

    def OnExit(self, event):
        self.Close()

    def OnChecked(self, event):
        cb = event.GetEventObject()
        if cb == self.grayBox:
            self.redBox.SetValue(False)
            self.greenBox.SetValue(False)
            self.blueBox.SetValue(False)
        elif cb == self.redBox:
            self.grayBox.SetValue(False)
            self.greenBox.SetValue(False)
            self.blueBox.SetValue(False)
        elif cb == self.greenBox:
            self.grayBox.SetValue(False)
            self.redBox.SetValue(False)
            self.blueBox.SetValue(False)
        elif cb == self.blueBox:
            self.grayBox.SetValue(False)
            self.redBox.SetValue(False)
            self.greenBox.SetValue(False)

# Video frame in panel wxPython


class VideoFrame(wx.Panel):

    def __init__(self, parent, w, h):
        wx.Panel.__init__(self, parent, wx.ID_ANY, (0, 0), (w, h))
        self.startBool = False
        self.videoMode = "default"
        self.width = int(w)
        self.height = int(h)
        self.timer = wx.Timer(self)
        self.timer.Start(1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

        self.Bind(wx.EVT_SIZE, self.Resize)

    @ property
    def Width(self):
        return self.width

    @ Width.setter
    def Width(self, value):
        self.width = value
        self.Refresh()

    @ property
    def Height(self):
        return self.height

    @ Height.setter
    def Height(self, value):
        self.height = value
        self.Refresh()

    @ property
    def VideoMode(self):
        return self.videoMode

    @ VideoMode.setter
    def VideoMode(self, value):
        self.videoMode = value

    @ property
    def CamNumber(self):
        return self.camNum

    @ CamNumber.setter
    def CamNumber(self, value):
        self.camNum = str(value)
        self.capture = cv2.VideoCapture(int(value))
        self.startBool = True

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        if self.startBool:
            ret, frame = self.capture.read()
            if ret:
                # b, g, r = cv2.split(frame)
                frame = cv2.resize(frame, (self.width, self.height))
                if self.videoMode == "default":
                    vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif self.videoMode == "gray":
                    # vframe = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    vframe = cv2.cvtColor(frame, cv2.IMREAD_GRAYSCALE)
                    vframe = cv2.threshold(vframe, 127, 255, 0)
                    # vframe = cv2.GaussianBlur(vframe, (9, 9), 0)
                elif self.videoMode == "red":
                    vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
                elif self.videoMode == "green":
                    vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                elif self.videoMode == "blue":
                    # vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    # define range of blue color in HSV
                    lower_blue = np.array([110, 50, 50])
                    upper_blue = np.array([130, 255, 255])
                    # Threshold the HSV image to get only blue colors
                    mask = cv2.inRange(hsv, lower_blue, upper_blue)
                    # Bitwise-AND mask and original image
                    vframe = cv2.bitwise_and(frame, frame, mask=mask)
                print(vframe.shape)
                vframe = cv2.putText(vframe, self.camNum, (self.Width - 100, self.Height - 70),
                                     cv2.FONT_HERSHEY_SIMPLEX, 1, (10, 10, 10), 2, cv2.LINE_AA)
                vframe = cv2.flip(vframe, 1)
            self.bmp = wx.BitmapFromBuffer(self.width, self.height, vframe)
            # self.bmp.CopyFromBuffer(vframe)
            self.Refresh()

    def Resize(self, event):
        self.width, self.height = self.GetSize()
