import wx
import cv2
import math
import numpy as np
from wx.lib.imageutils import grayOut


class MainFrame(wx.Frame):
    def __init__(self, title):
        super().__init__(None, title=title)
        self.StatusBar = self.CreateStatusBar()
        self.StatusBar.SetStatusText(
            "Здесь отобразится последнее применённое действие")

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

        self.cameraSelection = wx.ComboBox(panel, pos=(
            50, 30), choices=self.camName, style=wx.CB_READONLY)
        self.cameraSelection.SetSelection(0)
        hbox.Add(self.cameraSelection, proportion=1,
                 flag=wx.UP | wx.RIGHT | wx.LEFT, border=2)

        self.grayBox = wx.CheckBox(panel, label="Gray")
        hbox.Add(self.grayBox, proportion=1, flag=wx.UP, border=2)
        self.redBox = wx.CheckBox(panel, label="Red")
        hbox.Add(self.redBox, proportion=1, flag=wx.UP, border=2)
        self.greenBox = wx.CheckBox(panel, label="Green")
        hbox.Add(self.greenBox, proportion=1, flag=wx.UP, border=2)
        self.blueBox = wx.CheckBox(panel, label="Blue")
        hbox.Add(self.blueBox, proportion=1, flag=wx.UP, border=2)
        self.faceBox = wx.CheckBox(panel, label="Face")
        hbox.Add(self.faceBox, proportion=1, flag=wx.UP, border=2)
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
        if self.faceBox.GetValue():
            self.VideoFrame.FaceBool = True
            mode = "обнаружение лиц, "
        else:
            self.VideoFrame.FaceBool = False
            mode = ""

        if self.grayBox.GetValue():
            self.VideoFrame.VideoMode = "gray"
            mode += "оттенки серого | GRAYSCALE"
        elif self.redBox.GetValue():
            self.VideoFrame.VideoMode = "red"
            mode += "только красный цвет | RED"
        elif self.greenBox.GetValue():
            self.VideoFrame.VideoMode = "green"
            mode += "только зелёный цвет | GREEN"
        elif self.blueBox.GetValue():
            self.VideoFrame.VideoMode = "blue"
            mode += "только синий цвет | BLUE"
        else:
            self.VideoFrame.VideoMode = "default"
            mode += "все цвета | RGB"

        self.StatusBar.SetStatusText(
            str(self.cameraSelection.Value) + " была включена в режиме - " + mode)
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
        self.faceModel = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    @ property
    def FaceBool(self):
        return self.faceBool

    @ FaceBool.setter
    def FaceBool(self, value):
        self.faceBool = value

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
                    vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Ужасно медленный вариант
                    # for i in range(self.height):
                    #     for j in range(self.width):
                    #         blue = vframe[i, j, 0]
                    #         green = vframe[i, j, 1]
                    #         red = vframe[i, j, 2]
                    #         grayscale = blue * 0.114 + green * 0.587 + red * 0.299
                    #         vframe[i, j] = grayscale

                elif self.videoMode == "red":
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    lower_red = np.array([-10, 50, 50])
                    upper_red = np.array([10, 255, 255])
                    mask = cv2.inRange(hsv, lower_red, upper_red)
                    vframe = cv2.bitwise_and(frame, frame, mask=mask)
                    vframe = cv2.cvtColor(vframe, cv2.COLOR_BGR2RGB)
                elif self.videoMode == "green":
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    lower_green = np.array([50, 50, 50])
                    upper_green = np.array([70, 255, 255])
                    mask = cv2.inRange(hsv, lower_green, upper_green)
                    vframe = cv2.bitwise_and(frame, frame, mask=mask)
                    vframe = cv2.cvtColor(vframe, cv2.COLOR_BGR2RGB)
                elif self.videoMode == "blue":
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    # define range of blue color in HSV
                    lower_blue = np.array([110, 50, 50])
                    upper_blue = np.array([130, 255, 255])
                    # Threshold the HSV image to get only blue colors
                    mask = cv2.inRange(hsv, lower_blue, upper_blue)
                    # Bitwise-AND mask and original image
                    vframe = cv2.bitwise_and(frame, frame, mask=mask)
                    vframe = cv2.cvtColor(vframe, cv2.COLOR_BGR2RGB)

                if self.FaceBool:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.faceModel.detectMultiScale(gray, 1.1, 19)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(vframe, (x, y),
                                      (x+w, y+h), (0, 255, 0), 2)

                # print(vframe.shape)
                vframe = cv2.putText(vframe, self.camNum, (self.Width - 100, self.Height - 70),
                                     cv2.FONT_HERSHEY_SIMPLEX, 1, (10, 10, 10), 2, cv2.LINE_AA)
                # vframe = cv2.flip(vframe, 1)
                self.bmp = wx.BitmapFromBuffer(self.width, self.height, vframe)
            self.Refresh()

    def Resize(self, event):
        self.width, self.height = self.GetSize()
