import logging

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.WARNING)

## stdout logging for debugging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
##
logger = logging.getLogger('main')


import main_presenter
import projector_presenter
import config_presenter

def main():
    mainPresenter = main_presenter.Main_Presenter()
    configPresenter = config_presenter.Config_Presenter(mainPresenter.view)
    projectorPresenter = projector_presenter.Projector_Presenter(mainPresenter.view)

    mainPresenter.view.start()

if __name__ == '__main__':
    main()
