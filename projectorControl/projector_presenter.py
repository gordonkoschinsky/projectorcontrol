import logging
logger = logging.getLogger('projector_presenter')

import projector_model

from threadsafepub import pub as tpub
from pubsub import pub


class Projector_Presenter(object):
    def __init__(self, view):
        self._bindEvents()

        self.model = None
        self.view = view

    def _bindEvents(self):
        pub.subscribe(self._initModel, 'projector.view.ready')
        pub.subscribe(self._initModel, 'main.view.started')

        pub.subscribe(self._onConnection, 'projector.model.connection.ok')
        pub.subscribe(self._onNoConnection, 'projector.model.connection.error')
        pub.subscribe(self._onResponseError, 'projector.model.response.error')

        pub.subscribe(self._onPowered, 'projector.model.power.on')
        pub.subscribe(self._onUnpowered, 'projector.model.power.off')

        pub.subscribe(self._onShutterOpen, 'projector.model.shutter.open')
        pub.subscribe(self._onShutterClosed, 'projector.model.shutter.closed')

        pub.subscribe(self._onShutterToggled, 'projector.view.button.shutter')
        pub.subscribe(self._onPowerToggled, 'projector.view.button.power')
        pub.subscribe(self._onPowerOffConfirmed, 'projector.view.confirmed.poweroff')

        pub.subscribe(self._onCooling, 'projector.model.cooling.inprogress')
        pub.subscribe(self._onCoolingFinished, 'projector.model.cooling.finished')

        pub.subscribe(self._onValidConfigAnnounced, 'config.model.config.valid')

    def _initModel(self):
        self.model = projector_model.Projector()

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

    def _onValidConfigAnnounced(self, getConfig):
        self.model.configure(getConfig())

