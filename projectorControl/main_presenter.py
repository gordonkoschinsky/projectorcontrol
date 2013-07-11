import logging
logger = logging.getLogger('main_presenter')

import main_view
#import main_model    # there is no main model as of now.

from pubsub import pub
from threadsafepub import pub as tpub


class Main_Presenter(object):
    def __init__(self):
        self._bindEvents()

        self.model = None
        self.view = main_view.Main_View()

    def _bindEvents(self):
        pub.subscribe(self._initModel, 'main.view.started')

        pub.subscribe(self._onValidConfigAnnounced, 'config.model.config.valid')

    def _initModel(self):
        tpub.sendMessage('projector.view.ready')
        tpub.sendMessage('config.view.ready')
        #self.model = main_model.Main()

    def _onValidConfigAnnounced(self, getConfig):
        self.view.configure(getConfig())
