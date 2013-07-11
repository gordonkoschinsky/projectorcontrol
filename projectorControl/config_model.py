import logging
logger = logging.getLogger("config_model")

from pubsub import pub

import ConfigParser

CONFIG_FILE = "projector.ini"


class Config(object):
    def __init__(self):
        # Define the names of the config options
        self.options = {
            'projector_host': None,
            'projector_user': None,
            'projector_password': None,
            'ping_interval': 5
        }

        self.configured = False
        self.configParser = ConfigParser.SafeConfigParser()

    def readConfig(self, configFile):
        logger.info("Opening config file {}".format(configFile))

        # Load the configuration file
        if len(self.configParser.read(configFile)) == 0:
            pub.sendMessage('config.model.file.error')
            logger.error("Could NOT open config file {}".format(configFile))
            return

        try:
            for name in self.options:
                self.options[name] = self.configParser.get('projector', name)
                logger.debug('config:  %-15s = %r' % (name, self.options[name]))
        except ConfigParser.Error as e:
            pub.sendMessage('config.model.file.error')
            logger.error("Error while parsing config file {}: {}".format(configFile, e))
            self.configured = False
            return

        self.configured = True
        pub.sendMessage('config.model.file.ok')
        pub.sendMessage('config.model.config.valid', getConfig=self.getConfig)
        logger.info("config file {} parsed sucessfully".format(configFile))

    def getConfig(self):
        return self.options

