import logging
logger = logging.getLogger("controller")

from threadsafepub import pub as tpub

import ConfigParser
import requests
from time import sleep
import threading

CONFIG_FILE = "projector.ini"

class Projector(object):
    def __init__(self):
        logger.debug("Initialising model")
        self.initConfig()
        self.readConfig()
        self.shutdown = False
        self.pinger = threading.Thread(target=self.statusPinger)
        self.pinger.daemon = True
        self.pinger.start()

    def initConfig(self):
        self.configParser = ConfigParser.SafeConfigParser()
        self.configured = False

    def readConfig(self):
        logger.debug("Opening config file {}".format(CONFIG_FILE))

        # Define the names of the options
        option_names = [
            'projector_url',
            'projector_user',
            'projector_password',
            ]

        # Load the configuration file
        if len(self.configParser.read(CONFIG_FILE)) == 0:
            tpub.sendMessage('model.state.message', message="Config-File konnte nicht gelesen werden", color='red')
            logger.error("Could NOT open config file {}".format(CONFIG_FILE))
            return

        try:
            for name in option_names:
                value = self.configParser.get('projector', name)
                logger.debug('config:  %-15s = %r' % (name, value))
        except ConfigParser.Error as e:
            tpub.sendMessage('model.state.message', message="Fehler beim Lesen des Config-Files.", color='red')
            logger.error("Error while parsing config file {}: {}".format(CONFIG_FILE, e))
            return

        self.configured = True
        tpub.sendMessage('model.state.message', message="Config-File erfolgreich gelesen.")
        logger.debug("config file {} parsed sucessfully".format(CONFIG_FILE))

    def statusPinger(self):
        while not self.shutdown:
            logger.debug("Pinging host")
            self.requestStatus()
            sleep(5)

    def requestStatus(self):
        try:
            requests.get(self.configParser.get('projector','projector_url'))
        except requests.RequestException as e:
            tpub.sendMessage('model.state.message', message="Fehler bei Verbindung mit dem Projektor", color='red')
            logger.error("Request Error: {}".format(e))
            self.announce_NoConnection()

    def announce_NoConnection(self):
        tpub.sendMessage('model.connection.error')
        logger.debug("Announcing: no connection established")
