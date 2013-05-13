import logging
logger = logging.getLogger('controller')

import view
import model

from threadsafepub import pub as tpub
from pubsub import pub


class Controller(object):
    def __init__(self):
        self._bindEvents()

        self.model = None
        self.view = view.View()
        self.view.start()

    def _bindEvents(self):
        pub.subscribe(self._initApp, 'view.ready')

        pub.subscribe(self._onModelConfigfileError, 'model.config.file.error')
        pub.subscribe(self._onModelConfigfileOK, 'model.config.file.ok')

        pub.subscribe(self._onConnection, 'model.connection.ok')
        pub.subscribe(self._onNoConnection, 'model.connection.error')
        pub.subscribe(self._onResponseError, 'model.response.error')

        pub.subscribe(self._onPowered, 'model.power.on')
        pub.subscribe(self._onUnpowered, 'model.power.off')

        pub.subscribe(self._onShutterOpen, 'model.shutter.open')
        pub.subscribe(self._onShutterClosed, 'model.shutter.closed')

        pub.subscribe(self._onShutterToggled, 'view.button.shutter')
        pub.subscribe(self._onPowerToggled, 'view.button.power')
        pub.subscribe(self._onPowerOffConfirmed, 'view.confirmed.poweroff')

        pub.subscribe(self._onCooling, 'model.cooling.inprogress')
        pub.subscribe(self._onCoolingFinished, 'model.cooling.finished')

    def _initApp(self):
        self.model = model.Projector()

    def _onModelConfigfileError(self):
        self.view.disableView()
        tpub.sendMessage('controller.state.message', message="Config-File konnte nicht gelesen werden", color='red')

    def _onModelConfigfileOK(self):
        tpub.sendMessage('controller.state.message', message="Config-File erfolgreich gelesen.")

    def _onNoConnection(self):
        self.view.disableView()
        #tpub.sendMessage('controller.state.message', message="Fehler bei Verbindung mit dem Projektor", color='red')

    def _onConnection(self):
        self.view.enableView()
        #tpub.sendMessage('controller.state.message', message="Verbindung mit dem Projektor OK", color='green')

    def _onResponseError(self):
        tpub.sendMessage('controller.state.message', message="Daten vom Projektor FEHLERHAFT", color='red')

    def _onPowered(self):
        self.view.updateState(power=True)
        self.view.enableShutter()

    def _onUnpowered(self):
        self.view.updateState(power=False)
        self.view.disableShutter()

    def _onShutterClosed(self):
        self.view.updateState(shutter=False)

    def _onShutterOpen(self):
        self.view.updateState(shutter=True)

    def _onPowerToggled(self):
        if self.model.powered:
            self.view.confirmPowerOff()
        else:
            self.model.powerOn()

    def _onPowerOffConfirmed(self):
        self.model.powerOff()


    def _onShutterToggled(self):
        self.model.toggleShutter()

    def _onCooling(self):
        self.view.signalCooling()
        self.view.disableView()

    def _onCoolingFinished(self):
        self.view.signalCooling(False)
        self.view.enableView()
