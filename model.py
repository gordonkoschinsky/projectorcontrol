import logging
logger = logging.getLogger("controller")

from threadsafepub import pub as tpub

import ConfigParser
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from time import sleep
import threading
import re

CONFIG_FILE = "projector.ini"
PING_INTERVAL = 5

class Projector(object):
    def __init__(self):
        # Define the names of the config options
        self.options = {
            'projector_host': None,
            'projector_user': None,
            'projector_password': None,
            'projector_status_path': None,
            'projector_status_params': None,
            'projector_command_path': None,
            'projector_command_power_off': None,
            'projector_command_power_on': None,
            'projector_command_shutter_close': None,
            'projector_command_shutter_open': None,
        }

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

        # Load the configuration file
        if len(self.configParser.read(CONFIG_FILE)) == 0:
            tpub.sendMessage('model.state.message', message="Config-File konnte nicht gelesen werden", color='red')
            logger.error("Could NOT open config file {}".format(CONFIG_FILE))
            return

        try:
            for name in self.options:
                self.options[name] = self.configParser.get('projector', name)
                logger.debug('config:  %-15s = %r' % (name, self.options[name]))
        except ConfigParser.Error as e:
            tpub.sendMessage('model.state.message', message="Fehler beim Lesen des Config-Files.", color='red')
            logger.error("Error while parsing config file {}: {}".format(CONFIG_FILE, e))
            self.configured = False
            return

        self.configured = True
        tpub.sendMessage('model.state.message', message="Config-File erfolgreich gelesen.")
        logger.debug("config file {} parsed sucessfully".format(CONFIG_FILE))

    def statusPinger(self):
        while not self.shutdown:
            if not self.configured:
                continue
            logger.debug("Pinging host")
            self.requestStatus()
            sleep(PING_INTERVAL)

    def requestStatus(self):
        try:
            response = requests.get(self.options['projector_host'] + self.options['projector_status_path'],
                         timeout = 1,
                         auth = HTTPBasicAuth(self.options['projector_user'],
                                            self.options['projector_password']
                                            ),
                         params = self.options['projector_status_params']
                         )
            logger.debug("{}".format(response.url))
            if self.parseStatus(response.text):
                self.announce_connection()
            else:
                self.announce_noConnection()
        except requests.RequestException as e:
            logger.error("Request Error: {}".format(e))
            self.announce_noConnection()

    def parseStatus(self, status_html):
        logger.debug(status_html)
        soup = BeautifulSoup(status_html)

        text = soup.get_text()
        #logger.debug(text)

        # TODO: Match pattern with regexp -> parse into status vars
        regexp_projector = re.compile('.*PROJECTOR TYPED3500.*')
        match = regexp_projector.match(text)
        if match:
            return True
        return False
        #logger.debug(match)

    def announce_noConnection(self):
        tpub.sendMessage('model.connection.error')
        logger.debug("Announcing: no connection established")

    def announce_connection(self):
        tpub.sendMessage('model.connection.ok')
        logger.debug("Announcing: connection established")
