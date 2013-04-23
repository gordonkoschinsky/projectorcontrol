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
        pub.subscribe(self._initModel, 'view.ready')
        pub.subscribe(self._onConnection, 'model.connection.ok')
        pub.subscribe(self._onNoConnection, 'model.connection.error')

    def _onNoConnection(self):
        self.view.disableView()
        tpub.sendMessage('model.state.message', message="Fehler bei Verbindung mit dem Projektor", color='red')

    def _onConnection(self):
        self.view.enableView()
        tpub.sendMessage('model.state.message', message="Verbindung mit dem Projektor OK", color='green')

    def _initModel(self):
        self.model = model.Projector()


_controller = Controller()
