import wx
import gui_statusbar

import logging
from wxLogHandler import WxLogHandler

from pubsub import pub
from threadsafepub import pub as tpub

# 1. disabling control widgets and status widgets until READY event is fired, polled by tpub
# from our control thread
# 2. enable control and status, data was send by controller with the READY event
#
#
#
#


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 500))

        # WIDGETS
        self.panel = wx.Panel(self)

        logArea = wx.TextCtrl(self.panel,
                              style=
                              wx.TE_MULTILINE |
                              wx.TE_READONLY |
                              wx.TE_RICH2)

        self.sb = gui_statusbar.ColoredStatusBar(parent=self, fieldCount=2)
        self.SetStatusBar(self.sb)

        self.button_ShutterToggle = wx.Button(self.panel, label="Shutter ZU")
        self.button_ShutterToggle.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.staticText_ShutterState = wx.StaticText(self.panel, label="Shutter AUF", style=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        self.staticText_ShutterState.SetBackgroundColour('green')
        self.staticText_ShutterState.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        # SIZERS
        topSizer = wx.BoxSizer(wx.VERTICAL)

        shutterSizer = wx.BoxSizer(wx.HORIZONTAL)
        shutterSizer.Add(self.button_ShutterToggle, proportion=1, flag=wx.EXPAND)
        shutterSizer.Add(self.staticText_ShutterState, proportion=1,  flag=wx.EXPAND | wx.ALL)

        logSizer = wx.BoxSizer(wx.HORIZONTAL)
        logSizer.Add(logArea, proportion=1, flag=wx.EXPAND | wx.ALL)

        topSizer.Add(shutterSizer, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(logSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        self.panel.SetSizer(topSizer)

        # SETUP
        self.initLogging(logArea)

        # EVENTS
        #button_S1green.Bind(wx.EVT_BUTTON, self.onS1green)
        self.Bind(wx.EVT_IDLE, self.onIdle)

        self.panel.Layout()
        self.disableView()
        self.Show()

    def initLogging(self, logCtrl):
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        handler = WxLogHandler(logCtrl)
        handler.setFormatter(logging.Formatter('%(levelname)s | %(name)s | %(message)s [@ %(asctime)s in %(filename)s:%(lineno)d]'))
        rootLogger.addHandler(handler)
        rootLogger.debug("Logging initialized")

    def disableView(self):
        self.button_ShutterToggle.Disable()
        self.button_ShutterToggle.SetLabel("Shutter")
        self.staticText_ShutterState.SetBackgroundColour('grey')
        self.staticText_ShutterState.SetLabel(" - - - ")

    def onIdle(self, event):
        #logging.debug("IDLE")
        tpub.poll()


class View(object):
    def __init__(self):
        self.app = wx.App(redirect=0)
        self.mainframe = MainFrame(None, 'Kammerspiele ProjectorControl')
        pub.sendMessage('view.ready')

    def start(self):
        pub.sendMessage('view.started')
        self.app.MainLoop()

    def disableView(self):
        self.mainframe.disableView()

if __name__ == '__main__':
    View().start()
