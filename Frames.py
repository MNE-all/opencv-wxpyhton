import cv2
import wx
import math


class MainFrame(wx.Frame):
    def __init__(self, title):
        super().__init__(None, title=title)
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
        self.acceptBtn = wx.Button(panel, label="Принять")
        hbox.Add(self.acceptBtn, proportion=1, flag=wx.UP | wx.RIGHT, border=2)

        vbox.Add(hbox, flag=wx.EXPAND | wx.DOWN, border=2)

        # Считает количество подклюшенных камер
        self.cap = []
        max_tested = 100
        for i in range(max_tested):
            temp_camera = cv2.VideoCapture(i)
            if temp_camera.isOpened():
                temp_camera.release()
                self.cap.append(cv2.VideoCapture(i))
                continue
            self.amount = i
            break

        # Инициализация таблицы с камерами
        h, w = hbox.GetSize()

        self.campanels = []
        self.side = int(math.ceil(math.sqrt(self.amount)))
        grid = wx.GridSizer(self.side, self.side, 1, 1)
        for i in range(self.amount):
            self.cap[i] = cv2.VideoCapture(i)
            self.campanels.append(VideoFrame(
                panel, self.cap[i], int(self.W/self.side), int(self.H/self.side - 52), i))

            grid.Add(self.campanels[i], wx.ID_ANY, wx.EXPAND)

        vbox.Add(grid)
        panel.SetSizer(vbox)

        self.acceptBtn.Bind(wx.EVT_BUTTON, self.AcceptVideoMode)
        self.Bind(wx.EVT_MENU, self.OnExit, self.exitItem)
        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)
        self.Show()

    def AcceptVideoMode(self, event):
        if self.grayBox.GetValue():
            for i in range(self.amount):
                self.campanels[i].VideoMode = "gray"
        elif self.redBox.GetValue():
            for i in range(self.amount):
                self.campanels[i].VideoMode = "red"
        elif self.greenBox.GetValue():
            for i in range(self.amount):
                self.campanels[i].VideoMode = "green"
        elif self.blueBox.GetValue():
            for i in range(self.amount):
                self.campanels[i].VideoMode = "blue"
        else:
            for i in range(self.amount):
                self.campanels[i].VideoMode = "default"

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

    def __init__(self, parent, capture, w, h, camNum):
        self.camNum = str(camNum)
        self.videoMode = "default"
        wx.Panel.__init__(self, parent, wx.ID_ANY, (0, 0), (w, h))
        self.width = int(w)
        self.height = int(h)
        self.capture = capture
        ret, frame = self.capture.read()
        frame = cv2.resize(frame, (self.width, self.height), cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bmp = wx.BitmapFromBuffer(self.width, self.height, frame)
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

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            b, g, r = cv2.split(frame)
            frame = cv2.resize(frame, (self.width, self.height))
            if self.videoMode == "default":
                vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elif self.videoMode == "gray":
                vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                vframe = cv2.GaussianBlur(vframe, (9, 9), 0)
            elif self.videoMode == "red":
                vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
            elif self.videoMode == "green":
                vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            elif self.videoMode == "blue":
                vframe = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
            vframe = cv2.putText(
                vframe, self.camNum, (self.Width - 100, self.Height - 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (10, 10, 10), 2, cv2.LINE_AA)
            self.bmp.CopyFromBuffer(vframe)
            self.Refresh()

    def Resize(self, event):
        self.width, self.height = self.GetSize()
