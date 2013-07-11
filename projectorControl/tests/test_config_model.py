import projectorControl.config_model
import unittest
from projectorControl.tests.pubsub_test_mixin import PubsubTestMixin

import os
import mock

class Test_ConfigModel(PubsubTestMixin, unittest.TestCase):
    def setUp(self):
        self.model = projectorControl.config_model.Config()

    def tearDown(self):
        self.stopRecordingEvents()

    def test_should_announce_UNsuccesful_configuration_opening_and_be_unconfigured(self):
        # arrange
        self.model.configParser.read = lambda x:[] # mocking unsucessful ConfigParser.read call
        self.startRecordingEvents()

        # act
        self.model.readConfig("bogusfilename")

        # assert
        self.assertFired('config.model.file.error')
        self.assertFalse(self.model.configured)

    def test_should_announce_succesful_configuration_parsing_and_be_configured(self):
        # arrange
        self.model.configParser.read = lambda x:['bogusfilename'] # mocking sucessful ConfigParser.read call
        self.model.configParser.get = lambda x,y: 'bogusconfigvalue' # mocking sucessful ConfigParser.get call

        self.startRecordingEvents()

        # act
        self.model.readConfig("bogusfilename")

        # assert
        self.assertFired('config.model.file.ok')
        self.assertTrue(self.model.configured)

    def test_should_return_valid_config_via_announced_callback_method(self):
        # arrange
        self.model.configParser.read = lambda x:['bogusfilename'] # mocking sucessful ConfigParser.read call
        self.model.configParser.get = lambda x,y: 'bogusconfigvalue' # mocking sucessful ConfigParser.get call

        def listener_with_args(getConfig):
            listener_with_args.called = True
            listener_with_args.config = getConfig()
        listener_with_args.called = False
        listener_with_args.config = None

        from pubsub import pub
        pub.subscribe(listener_with_args, 'config.model.config.valid')

        self.startRecordingEvents()

        # act
        self.model.readConfig("bogusfilename")

        # assert
        self.assertFired('config.model.config.valid')
        self.assertTrue(listener_with_args.called)
        self.assertTrue('bogusconfigvalue' in listener_with_args.config.values())

    def test_should_announce_UNsuccesful_configuration_parsing_and_be_unconfigured(self):
        # arrange
        import ConfigParser
        self.model.configParser.get = mock.Mock(spec=ConfigParser.SafeConfigParser)
        self.model.configParser.get.side_effect = ConfigParser.Error("Should fail")
        self.model.configParser.read = lambda x:['bogusfilename'] # mocking sucessful ConfigParser.read call
        self.startRecordingEvents()

        # act
        self.model.readConfig("bogusfilename")

        # assert
        self.assertFired('config.model.file.error')
        self.assertFalse(self.model.configured)
