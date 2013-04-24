# -*- coding: UTF-8 -*-
import wx
import wx.lib.buttons as buttons
import gui_statusbar

import logging
from wxLogHandler import WxLogHandler

from pubsub import pub
from threadsafepub import pub as tpub

logger = logging.getLogger('view')


class MainFrame(wx.Frame):
    def __init__(self, parent, title='Kammerspiele ProjectorControl'):
        wx.Frame.__init__(self, parent, title=title, size=(800, 500))

        #
        # WIDGETS
        #
        self.panel = wx.Panel(self)

        # Log

        self.logArea = wx.TextCtrl(self.panel,
                              style=
                              wx.TE_MULTILINE |
                              wx.TE_READONLY |
                              wx.TE_RICH2)

        checkbox_showLog = wx.CheckBox(self.panel, label="Zeige Log")
        checkbox_showLog.SetValue(True)

        # Status bar
        self.sb = gui_statusbar.ColoredStatusBar(parent=self, fieldCount=2)
        self.SetStatusBar(self.sb)

        # Shutter control
        self.button_ShutterToggle = buttons.GenButton(self.panel, label=u"Shutter öffnen",
                                             style=wx.BORDER_NONE)
        self.button_ShutterToggle.BackgroundColour = "red"
        self.button_ShutterToggle.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Power control
        self.button_PowerToggle = buttons.GenButton(self.panel, label="Anschalten",
                                             style=wx.BORDER_NONE)
        self.button_PowerToggle.BackgroundColour = "red"
        self.button_PowerToggle.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Cooling indicator
        self.blinkingTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.flashBackground, self.blinkingTimer)

        #
        # SIZERS
        #
        topSizer = wx.BoxSizer(wx.VERTICAL)

        shutterSizer = wx.BoxSizer(wx.HORIZONTAL)
        shutterSizer.Add(self.button_ShutterToggle, proportion=1, flag=wx.EXPAND)

        powerSizer = wx.BoxSizer(wx.HORIZONTAL)
        powerSizer.Add(self.button_PowerToggle, proportion=1, flag=wx.EXPAND)

        logSizer = wx.BoxSizer(wx.HORIZONTAL)
        logSizer.Add(self.logArea, proportion=1, flag=wx.EXPAND | wx.ALL)

        topSizer.Add(shutterSizer, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(powerSizer, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(logSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(checkbox_showLog, flag=wx.ALL | wx.EXPAND, border=5)

        self.panel.SetSizer(topSizer)

        # SETUP
        self.initLogging(self.logArea)

        # EVENTS
        checkbox_showLog.Bind(wx.EVT_CHECKBOX, self.onShowLogChecked)
        self.button_ShutterToggle.Bind(wx.EVT_BUTTON, self.onShutterToggle)
        self.button_PowerToggle.Bind(wx.EVT_BUTTON, self.onPowerToggle)
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

    def disableShutter(self):
        self.button_ShutterToggle.Disable()
        self.button_ShutterToggle.BackgroundColour = 'light grey'

    def enableShutter(self):
        self.button_ShutterToggle.Enable()

    def disableView(self):
        self.disableShutter()
        self.button_PowerToggle.Disable()
        self.button_PowerToggle.BackgroundColour = 'light grey'

    def enableView(self):
        self.button_PowerToggle.Enable()

    def updatePower(self, state):
        self.button_PowerToggle.BackgroundColour = ('red', 'green')[state]
        self.button_PowerToggle.SetLabel(("Anschalten", "Ausschalten")[state])
        self.Refresh()

    def updateShutter(self, state):
        self.button_ShutterToggle.BackgroundColour = ('red', 'green')[state]
        self.button_ShutterToggle.SetLabel((u"Shutter öffnen", u"Shutter schließen")[state])
        self.Refresh()

    def blinkBackground(self):
        self.blinkingTimer.Start(500)

    def unblinkBackground(self):
        self.blinkingTimer.Stop()

    def flashBackground(self, event=None):
        self.BackgroundColour = "yellow"
        self.Refresh()
        wx.CallLater(250, self.restoreBackground)

    def restoreBackground(self):
        self.BackgroundColour = wx.NullColor
        self.Refresh()

    def onIdle(self, event):
        tpub.poll()

    def onShowLogChecked(self, event):
        self.logArea.Shown = event.IsChecked()
        self.logArea.GetParent().Fit()
        self.logArea.GetParent().Layout()
        self.logArea.GetTopLevelParent().Fit()
        self.logArea.GetTopLevelParent().Layout()
        # TODO: Adjust frame height to log Area

    def onShutterToggle(self, event):
        pub.sendMessage('view.button.shutter')

    def onPowerToggle(self, event):
        pub.sendMessage('view.button.power')


class View(object):
    def __init__(self):
        self.app = wx.App(redirect=0)
        self.mainframe = MainFrame(None, 'Kammerspiele ProjectorControl')
        self.app.SetTopWindow(self.mainframe)
        pub.sendMessage('view.ready')

    def start(self):
        pub.sendMessage('view.started')
        self.app.MainLoop()

    def disableShutter(self):
        self.mainframe.disableShutter()

    def enableShutter(self):
        self.mainframe.enableShutter()

    def disableView(self):
        self.mainframe.disableView()

    def enableView(self):
        self.mainframe.enableView()

    def updateState(self, **kwargs):
        if 'power' in kwargs:
            self.mainframe.updatePower(kwargs['power'])

        if 'shutter' in kwargs:
            self.mainframe.updateShutter(kwargs['shutter'])

    def signalCooling(self, enable = True):
        if enable:
            self.mainframe.blinkBackground()
        else:
            self.mainframe.unblinkBackground()

if __name__ == '__main__':
    View().start()
