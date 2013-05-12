# -*- coding: UTF-8 -*-
import logging
from wxLogHandler import WxLogHandler
logger = logging.getLogger('view')

import wx
import wx.lib.buttons as buttons
from wx.lib.embeddedimage import PyEmbeddedImage
import gui_statusbar

from pubsub import pub
from threadsafepub import pub as tpub

from collections import OrderedDict

import win32con


video_projector = PyEmbeddedImage(
    "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")


class LogFrame(wx.MiniFrame):
    def __init__(self, parent):
        wx.MiniFrame.__init__(self,
                              parent,
                              title="ProjectorControl Log",
                              style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)

        panel = wx.Panel(self)

        self.logArea = wx.TextCtrl(panel,
                              style=
                              wx.TE_MULTILINE |
                              wx.TE_READONLY |
                              wx.TE_RICH2)

        logLevels = OrderedDict()
        logLevels[logging.DEBUG] = logging.getLevelName(logging.DEBUG)
        logLevels[logging.INFO] = logging.getLevelName(logging.INFO)
        logLevels[logging.WARNING] = logging.getLevelName(logging.WARNING)
        logLevels[logging.ERROR] = logging.getLevelName(logging.ERROR)
        logLevels[logging.CRITICAL] = logging.getLevelName(logging.CRITICAL)

        self.CmbBoxLogLevel = wx.ComboBox(parent=panel, style=wx.CB_DROPDOWN | wx.CB_READONLY)

        for level, levelName in logLevels.items():
            self.CmbBoxLogLevel.Append(levelName, level)

        try:
            self.CmbBoxLogLevel.SetValue(logLevels[logging.getLogger().getEffectiveLevel()])
        except:
            # Unknown level, custom?
            pass

        stTxtLevelLabel = wx.StaticText(parent=panel, label="Log-Level:")

        # SIZER

        topSizer = wx.BoxSizer(wx.VERTICAL)

        logSizer = wx.BoxSizer(wx.HORIZONTAL)
        logSizer.Add(self.logArea, proportion=1, flag=wx.EXPAND | wx.ALL)

        levelSelectorSizer = wx.BoxSizer(wx.HORIZONTAL)
        levelSelectorSizer.Add(stTxtLevelLabel, flag=wx.CENTER | wx.LEFT, border=5)
        levelSelectorSizer.Add(self.CmbBoxLogLevel, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        topSizer.Add(logSizer, proportion=2, flag=wx.EXPAND, border=5)
        topSizer.Add(levelSelectorSizer, flag=wx.EXPAND, border=5)

        panel.SetSizer(topSizer)

        # EVENTS

        self.Bind(wx.EVT_COMBOBOX, self.OnSelectLogLevel)

    def OnSelectLogLevel(self, event):
        rootLogger = logging.getLogger()
        selectedLogLevel = self.CmbBoxLogLevel.GetClientData(event.GetSelection())
        rootLogger.setLevel(selectedLogLevel)

    def GetLogWidget(self):
        return self.logArea

class MainFrame(wx.Frame):
    def __init__(self, parent, title='Kammerspiele ProjectorControl'):
        wx.Frame.__init__(self, parent, title=title)

        self.SetMinSize((200, 150))

        self.SetIcon(video_projector.getIcon())

        # HOT KEYS

        # TODO: Make hotkeys configurable via .ini
        # TODO: Make separate shutter open and close hotkeys and thus refactor the
        # model api to support this
        # TODO: Make small programms that only fire a specific kex command, this
        # can be used by visio to control the shutter
        # TODO: Look into MIDI for python
        self.hotKeyId_Shutter = 100
        self.RegisterHotKey(
                    self.hotKeyId_Shutter,  #a unique ID for this hotkey
                    win32con.MOD_ALT,       #the modifier key
                    win32con.VK_F12)        #the key to watch for

        self.Bind(wx.EVT_HOTKEY, self.onShutterToggle, id=self.hotKeyId_Shutter)

        #
        # LOG FRAME
        #
        self.logFrame = LogFrame(self)

        #
        # WIDGETS
        #
        self.panel = wx.Panel(self)

        # Log
        self.checkbox_showLog = wx.CheckBox(self.panel, label="Zeige Log")
        self.checkbox_showLog.SetValue(False)

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

        topSizer.Add(shutterSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(powerSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        topSizer.Add(self.checkbox_showLog, flag=wx.ALL | wx.EXPAND, border=5)

        self.panel.SetSizer(topSizer)

        # SETUP
        self.initLogging(self.logFrame.GetLogWidget())

        # EVENTS
        self.checkbox_showLog.Bind(wx.EVT_CHECKBOX, self.onShowLogChecked)
        self.button_ShutterToggle.Bind(wx.EVT_BUTTON, self.onShutterToggle)
        self.button_PowerToggle.Bind(wx.EVT_BUTTON, self.onPowerToggle)
        self.logFrame.Bind(wx.EVT_CLOSE, self.onLogClosed)
        self.Bind(wx.EVT_IDLE, self.onIdle)

        self.panel.Fit()
        self.panel.Layout()
        self.SetSize((400, 200))

        self.disableView()
        self.Fit()
        self.Show()

    def initLogging(self, logCtrl):
        rootLogger = logging.getLogger()
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
        if not self.blinkingTimer.IsRunning():
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
        self.logFrame.Shown = event.IsChecked()

    def onShutterToggle(self, event):
        if self.button_ShutterToggle.Enabled:
            # check if enabled because the hotkey could still trigger even if disabled
            pub.sendMessage('view.button.shutter')

    def onPowerToggle(self, event):
        pub.sendMessage('view.button.power')

    def onLogClosed(self, event):
        self.checkbox_showLog.SetValue(False)
        self.logFrame.Hide()
        event.skip()


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
