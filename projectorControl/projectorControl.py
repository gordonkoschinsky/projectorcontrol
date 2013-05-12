import logging

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.WARNING)


logger = logging.getLogger('main')

import controller

_controller = controller.Controller()
