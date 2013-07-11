import projectorControl.projector_model
import unittest
from projectorControl.tests.pubsub_test_mixin import PubsubTestMixin

import os
import mock

class Test_ProjectorModel(PubsubTestMixin, unittest.TestCase):
    def setUp(self):
        self.model = projectorControl.projector_model.Projector()

        self.validConfig = {
            'projector_host': None,
            'projector_user': None,
            'projector_password': None,
            'ping_interval': 5
        }

    def tearDown(self):
        self.stopRecordingEvents()

    def test_should_be_configured_after_configuration_with_valid_config(self):
        # arrange

        # act
        self.model.configure(self.validConfig)

        # assert
        self.assertTrue(self.model.configured)

    def test_should_be_unconfigured_after_configuration_with_invalid_config(self):
        # arrange

        # act
        self.model.configure("bogusConfig")

        # assert
        self.assertFalse(self.model.configured)

    def test_should_be_unconfigured_after_configuration_with_missing_option(self):
        # arrange
        config = self.validConfig
        config.pop('projector_host')

        # act
        self.model.configure(config)

        # assert
        self.assertFalse(self.model.configured)
    #
    #def test_should_announce_succesful_configuration_parsing(self):
    #    # arrange
    #    self.model.configParser.read = lambda x:['bogusfilename'] # mocking sucessful ConfigParser.read call
    #    self.model.configParser.get = lambda x,y: 'bogusconfigvalue' # mocking UNsucessful ConfigParser.get call
    #
    #    self.startRecordingEvents()
    #
    #    # act
    #    self.model.readConfig("bogusfilename")
    #
    #    # assert
    #    self.assertFired('config.model.file.ok')
    #    self.assertTrue(self.model.configured)
    #
    #def test_should_announce_UNsuccesful_configuration_parsing(self):
    #    # arrange
    #    import ConfigParser
    #    self.model.configParser.get = mock.Mock(spec=ConfigParser.SafeConfigParser)
    #    self.model.configParser.get.side_effect = ConfigParser.Error("Should fail")
    #    self.model.configParser.read = lambda x:['bogusfilename'] # mocking sucessful ConfigParser.read call
    #    self.startRecordingEvents()
    #
    #    # act
    #    self.model.readConfig("bogusfilename")
    #
    #    # assert
    #    self.assertFired('config.model.file.error')
    #    self.assertFalse(self.model.configured)
