import wx

# from applet.gui.main_box import MainBox
from applet.gui.main_box2 import MainBox


def create_frame():
    app = wx.App()
    frame = MainBox()
    frame.Centre()
    frame.Show()

    app.MainLoop()


if __name__ == '__main__':
    create_frame()
