import cv2
import wx
import Frames


app = wx.App()
frame = Frames.MainFrame("Главная")
app.MainLoop()

cv2.destroyAllWindows()
