import logging
logger = logging.getLogger('controller')

import view
import model

from threadsafepub import pub as tpub
from pubsub import pub

import ConfigParser


class Controller(object):
    def __init__(self):
        self._bindEvents()

        self.model = None
        self.view = view.View()
        self.view.start()

    def _bindEvents(self):
        pub.subscribe(self._initModel, 'view.ready')
        pub.subscribe(self._noConnection, 'model.connection.error')

    def _noConnection(self):
        self.view.disableView()

    def _initModel(self):
        self.model = model.Projector()


_controller = Controller()
