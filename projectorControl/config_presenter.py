import logging
logger = logging.getLogger('config_presenter')

#import config_view
import config_model

from pubsub import pub


class Config_Presenter(object):
    def __init__(self, view):
        self._bindEvents()
        self.model = None
        self.view = view

    def _bindEvents(self):
        pub.subscribe(self._initModel, 'config.view.ready')

        pub.subscribe(self._onConfigfileError, 'config.model.file.error')
        pub.subscribe(self._onConfigfileOK, 'config.model.file.ok')

    def _initModel(self):
        self.model = config_model.Config()
        self.model.readConfig(config_model.CONFIG_FILE)

    def _onConfigfileError(self):
        self.view.disableView()
        self.view.generalMessage(message="Config-File konnte nicht gelesen werden", color='red')

    def _onConfigfileOK(self):
        self.view.generalMessage(message="Config-File erfolgreich gelesen.")

    def getConfigOptions(self, ):
        pass
