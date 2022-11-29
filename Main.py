import cv2
import wx
import math


class MainFrame(wx.Frame):
    def __init__(self, title):
        super().__init__(None, title=title)
        self.Maximize()
        self.W, self.H = self.GetSize()
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

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

        # Инициализация таблицы с камерами (пока что с кнопками)
        self.campanels = []
        self.side = int(math.ceil(math.sqrt(self.amount)))
        grid = wx.GridSizer(self.side, self.side, 1, 1)
        for i in range(self.amount):
            self.cap[i] = cv2.VideoCapture(i)
            self.campanels.append(VideoFrame(
                panel, self.cap[i], int(self.W/self.side), int(self.H/self.side)))

            grid.Add(self.campanels[i], wx.ID_ANY, wx.EXPAND)

        panel.SetSizer(grid)

        # self.Bind(wx.EVT_SIZE, self.Resize)
        self.Show()

    def Resize(self, event):
        self.W, self.H = self.GetSize()
        for i in range(self.amount):
            self.campanels[i].Resize(
                int(self.W/self.side), int(self.H/self.side))


class VideoFrame(wx.Panel):

    def __init__(self, parent, capture, w, h):
        wx.Panel.__init__(self, parent, wx.ID_ANY, (0, 0), (w, h))
        self.Width = int(w)
        self.Height = int(h)
        self.capture = capture
        ret, frame = self.capture.read()
        frame = cv2.resize(frame, (self.Width, self.Height), cv2.INTER_NEAREST)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.BitmapFromBuffer(self.Width, self.Height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.resize(frame, (self.Width, self.Height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()

    def Resize(self, w, h):
        self.Width = int(w)
        self.Height = int(h)
        # self.Refresh()


app = wx.App()
frame = MainFrame("Главная")
app.MainLoop()

cv2.destroyAllWindows()
