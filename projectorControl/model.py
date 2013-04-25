import logging
logger = logging.getLogger("model")

from threadsafepub import pub as tpub

import ConfigParser
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from time import sleep
import threading
import re

CONFIG_FILE = "projector.ini"


class Projector(object):
    projector_status_url_path = "/cgi-bin/projector_status.cgi"
    projector_status_query_string = "lang=e"
    projector_command_url_path = "/cgi-bin/proj_ctl.cgi"
    # complete query strings
    projector_command_power_off = "key=pow_off&lang=e&osd=on"
    projector_command_power_on = "key=pow_on&lang=e&osd=on"
    projector_command_shutter_close = "key=shutter_on&lang=e&osd=on"
    projector_command_shutter_open = "key=shutter_off&lang=e&osd=on"

    # the following regexp will be matched on the stripped responses from the
    # projector
    regexp_projector = re.compile('.*PROJECTOR TYPED3500.*')
    regexp_cooling = re.compile('.*Cooling...*')
    # beautiful soup instructions to extract the data we want out of the status response
    # these will be put into an "exec" instruction
    soup_power_state = compile("power = (True, False)\
                                [soup.find('td').find('td').find_next().find_next('font')['color'] \
                                =='#999999']",
                                '<string>',
                                'exec')

    soup_shutter_state = compile("shutter = (True, False)\
                                [soup.find_all('td')[6].find_all('font')[1]['color'] \
                                =='#999999']",
                                '<string>',
                                'exec')
    # TODO: The status scraping is insufficient if an error occurs, because it
    # only checks *one* condition of power and status, and assumes that when
    # this condition is not met, the other condition ist true.
    # In reality, if the response is mangled, the program assumes that everything
    # is still ok as long as the checked condition looks sane.
    # I leave this as it is for now, because I don't expect a closed system
    # like a video projector to change it's output often.

    def __init__(self):
        # Define the names of the config options
        self.options = {
            'projector_host': None,
            'projector_user': None,
            'projector_password': None,
            'ping_interval': 5
        }

        self.configured = False
        self.powered = False
        self.cooling = False
        self.shutter = False

        self.initConfig()
        self.readConfig()
        self.shutdown = False
        self.pinger = threading.Thread(target=self.statusPinger)
        self.pinger.daemon = True
        self.pinger.start()

    def initConfig(self):
        self.configParser = ConfigParser.SafeConfigParser()

    def readConfig(self):
        logger.info("Opening config file {}".format(CONFIG_FILE))

        # Load the configuration file
        if len(self.configParser.read(CONFIG_FILE)) == 0:
            tpub.sendMessage('model.config.file.error')
            logger.critical("Could NOT open config file {}".format(CONFIG_FILE))
            return

        try:
            for name in self.options:
                self.options[name] = self.configParser.get('projector', name)
                logger.debug('config:  %-15s = %r' % (name, self.options[name]))
        except ConfigParser.Error as e:
            tpub.sendMessage('model.config.file.error')
            logger.critical("Error while parsing config file {}: {}".format(CONFIG_FILE, e))
            self.configured = False
            return

        self.configured = True
        tpub.sendMessage('model.config.file.ok')
        logger.info("config file {} parsed sucessfully".format(CONFIG_FILE))

    def makeRequest(self, url, params):
        try:
            response = requests.get(url,
                         timeout = 3,
                         auth = HTTPBasicAuth(self.options['projector_user'],
                                            self.options['projector_password']
                                            ),
                         params = params
                         )
            logger.debug("Requesting {}".format(response.url))
            return response
        except requests.RequestException as e:
            logger.error("Request Error: {}".format(e))
            self.announce_noConnection()
            return None

    def statusPinger(self):
        while not self.shutdown:
            if not self.configured:
                sleep(1)
                continue
            logger.info("Pinging projector host")
            self.requestStatus()
            sleep(float(self.options['ping_interval']))

    def requestStatus(self):
        response = self.makeRequest(self.options['projector_host'] +
                         self.projector_status_url_path,
                         self.projector_status_query_string)

        if response is None:
            return False

        logger.debug("ping response status code {}".format(response.status_code))

        if response.status_code != 200:
            if response.status_code == 401:
                logger.error("Authentification error, check username and password")
            else:
                logger.error("General ping response error, code {}".format(response.status_code))
            self.announce_noConnection()
            return False

        if self.parseStatus(response.text):
            if not self.cooling:
                self.announce_connection()
        else:
            self.announce_noConnection()

    def parseStatus(self, status_html):
        soup = BeautifulSoup(status_html)
        text = soup.get_text()

        match = self.regexp_projector.search(text)
        if not match:
            logger.warning("Could not match the projector type to the status response.")
            return False

        # Execute the precompiled power state condition, limiting the namespace
        try:
            nsg, nsl = {"__builtins__": None, "False": False, "True": True}, {"soup": soup}
            exec(self.soup_power_state, nsg, nsl)
            self.powered = nsl['power']
            logger.info("Power is {}".format("ON" if nsl['power'] else "OFF"))
        except Exception as e:
            logger.warning("Error in Power response: {}".format(e))
            self.announce_erroneousResponse()
        if not self.cooling:
            if self.powered:
                self.announce_powered()
            else:
                self.announce_unpowered()

        if self.powered:
            # Execute the precompiled shutter state condition, limiting the namespace
            try:
                nsg, nsl = {"__builtins__": None, "False": False, "True": True}, {"soup": soup}
                exec(self.soup_shutter_state, nsg, nsl)
                self.shutter = nsl['shutter']
                logger.info("Shutter is {}".format("CLOSED" if nsl['shutter'] else "OPEN"))
                if not self.cooling:
                    if self.shutter:
                        self.announce_shutterClosed()
                    else:
                        self.announce_shutterOpen()
            except Exception as e:
                logger.warning("Error in Shutter response: {}".format(e))
                self.announce_erroneousResponse()
        return True

    def requestCommand(self, command_query_string):
        response = self.makeRequest(self.options['projector_host'] +
                         self.projector_command_url_path,
                         command_query_string)

        if response is None:
            return False

        logger.debug("command response status code {}".format(response.status_code))

        if response.status_code != 200:
            logger.error("General command response error, code {}".format(response.status_code))
            return False

        self.parseCommandResponse(response)

    def toggleShutter(self):
        if self.shutter:
            self.requestCommand(self.projector_command_shutter_open)
            if self.shutter:
                self.announce_shutterOpen()
        else:
            self.requestCommand(self.projector_command_shutter_close)
            if not self.shutter:
                self.announce_shutterClosed()

    def togglePower(self):
        if not self.cooling:
            if self.powered:
                self.requestCommand(self.projector_command_power_off)
            else:
                self.requestCommand(self.projector_command_power_on)

            if self.cooling:
                # power button is disabled while cooling,
                # make sure we don't miss the end of cooling
                coolingWatchdog = threading.Thread(target=self.coolingWatchdog)
                coolingWatchdog.daemon = True
                coolingWatchdog.start()

    def parseCommandResponse(self, response):
        # TODO Parse shutter response for FAST UI update
        soup = BeautifulSoup(response.text)
        text = soup.get_text()

        match = self.regexp_cooling.search(text)

        if match:
            logger.info("Still cooling...")
            self.announce_cooling()
            self.cooling = True
        else:
            # done cooling
            self.announce_coolingFinished()
            self.cooling = False

    def coolingWatchdog(self):
        watchCooling = True
        while watchCooling:
            self.requestCommand(self.projector_command_power_off)
            watchCooling = self.cooling
            sleep(2)

    def announce_noConnection(self):
        tpub.sendMessage('model.connection.error')
        logger.debug("Announcing: no connection established")

    def announce_connection(self):
        tpub.sendMessage('model.connection.ok')
        logger.debug("Announcing: connection established")

    def announce_erroneousResponse(self):
        tpub.sendMessage('model.response.error')
        logger.debug("Announcing: Error in projector response")

    def announce_powered(self):
        tpub.sendMessage('model.power.on')
        logger.debug("Announcing: Power ON")

    def announce_unpowered(self):
        tpub.sendMessage('model.power.off')
        logger.debug("Announcing: Power OFF")

    def announce_shutterClosed(self):
        tpub.sendMessage('model.shutter.closed')
        logger.debug("Announcing: Shutter closed")

    def announce_shutterOpen(self):
        tpub.sendMessage('model.shutter.open')
        logger.debug("Announcing: Shutter open")

    def announce_cooling(self):
        tpub.sendMessage('model.cooling.inprogress')
        logger.debug("Announcing: Cooling")

    def announce_coolingFinished(self):
        tpub.sendMessage('model.cooling.finished')
        logger.debug("Announcing: Cooling finished")

if __name__ == '__main__':
    logging.basicConfig()
    model = Projector()
    sleep(5)
