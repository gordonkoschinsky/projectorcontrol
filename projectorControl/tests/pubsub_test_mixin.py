'''
Mixin for unittest.TestCase
enables to test for fired events via pypubsub

Problems with this version:
- since unittest is creating a new instance of TestCase at run time for every
  test method found inside a TestCase class, a mixin instance and its
  notification handler instance will be created for every method, also. This
  means that there are many handlers that are notified if a message is sent by
  pubsub. If we fire an event in one test method, ALL handlers will get a
  notification and add the event to their log list. We have no way to reset
  those handlers to clear them when they are actually meant to be used in a test
  method.
As a quick solution, logging of events must now be enabled in the test functions
by calling self.startRecordingEvents. By default, the handlers won't record
events and thus won't log "foreign" events. You should call
self.stopRecordingEvents() in your tearDown() method, so the handler log list
won't be cluttered with the events that follow from "foreign" tests - if their
instance is still alive at this time, which I don't know.
'''
from pubsub import pub
import pubsub.utils.notification as notif


__unittest = True
# Needed so the stack frames of this mixin are hidden in
# the test result Traceback.

import logging

class MessageSendNotifationHandler(notif.INotificationHandler):
    '''A pubsub notification handler that logs sent messages into a list
    '''
    def __init__(self):
        self.messages = []
        self.topics = {}
        self.recording = False
        self.virginLog = True

    def notifySend(self, stage, topicObj, pubListener=None):
        if stage == 'pre' and self.recording:
            topic = topicObj.getName()
            self.messages.append(topicObj.getName())
            if topic in self.topics:
                self.topics[topic] += 1
            else:
                self.topics[topic] = 1

    def getMessages(self):
        return self.messages

    def getTopics(self):
        return self.topics

    def reset(self):
        self.messages = []


class PubsubTestMixin(object):
    def __init__(self, *args, **kwargs):
        super(PubsubTestMixin, self).__init__(*args, **kwargs)
        self.notificationHandler = MessageSendNotifationHandler()
        pub.addNotificationHandler(self.notificationHandler)
        pub.setNotificationFlags(sendMessage=True)

    def startRecordingEvents(self):
        self.notificationHandler.recording = True
        self.notificationHandler.virginLog = False

    def stopRecordingEvents(self):
        self.notificationHandler.recording = False

    def assertFired(self, topic, times=None):
        '''
        Fails if no message with the given topic was sent.
        If times is not None, the number the same topic has been fired must match
        the value of times. If times is None, the topic must been fired 1 or more
        times.
        '''
        if self.notificationHandler.virginLog:
            self.fail('PubSub events were never recorded! Call startRecordingEvents before asserting.')
        self.assertTrue(topic in self.notificationHandler.getMessages(), "pubSub message with topic '%s' expected but not fired (%s)" % (topic, self.notificationHandler.getMessages()))
        if times:
            self.assertEqual(self.notificationHandler.getTopics()[topic], times, "pubSub message with topic '%s' expected %s times but fired %s times (%s)" % (topic, times, self.notificationHandler.getTopics()[topic], self.notificationHandler.getMessages()))

    def assertNotFired(self, topic):
        self.assertFalse(topic in self.notificationHandler.getMessages(), "pubSub message with topic '%s' fired unexpectedly (%s)" % (topic, self.notificationHandler.getMessages()))

    def resetPubSubNotifier(self):
        '''
        clear all messages fired so far
        '''
        self.notificationHandler.reset()


#########################################
# Example usage AND unit tests for the mixin in one.
# Needs unittest2 to work in Python < 2.7
#########################################

import unittest


def sut_fires_some():
    pub.sendMessage("some")

def sut_fires_some_with_args():
    pub.sendMessage("somewithargs", argsToSend="someargs")

def sut_fires_another():
    pub.sendMessage("another")


class MixinTest(PubsubTestMixin, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MixinTest, self).__init__(*args, **kwargs)
        #PubsubTestMixin.__init__(self)
        #unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        pass

    def test_assertFired_whenExpectedEventFiredAndRecorded_passes(self):
        self.startRecordingEvents()
        sut_fires_some()
        self.assertFired("some")

    def test_assertFired_whenExpectedEventAndOthersAfterwardsFiredAndRecorded_passes(self):
        self.startRecordingEvents()
        sut_fires_some()
        sut_fires_another()
        self.assertFired("some")

    def test_assertFired_whenExpectedEventAndOthersBeforeFiredAndRecorded_passes(self):
        self.startRecordingEvents()
        sut_fires_another()
        sut_fires_some()
        self.assertFired("some")

    def test_assertFired_whenExpectedEventFiredMultipleTimesAndRecorded_passes(self):
        self.startRecordingEvents()
        sut_fires_some()
        sut_fires_some()
        sut_fires_some()
        self.assertFired("some")

    # The following test need to fail to be successful, since we
    # can't check for assertionErrors, because we are testing ourselves here, and every AssertionError
    # is catched by the TestCase and will immediately stop the test.

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_whenExpectedEventFiredAndNotRecorded_fails(self):
        sut_fires_some()
        self.assertFired("some")

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_whenExpectedEventFiredAndRecordingStopped_fails(self):
        self.startRecordingEvents()
        self.stopRecordingEvents()
        sut_fires_some()
        self.assertFired("some")

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_whenExpectedEventFiredAnotherRecordedAndRecordingStopped_fails(self):
        self.startRecordingEvents()
        sut_fires_another()()
        self.stopRecordingEvents()
        sut_fires_some()
        self.assertFired("some")

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_whenAnotherThanExpectedEventFiredAndRecording_fails(self):
        self.startRecordingEvents()
        sut_fires_another()
        self.assertFired("some")

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_whenRecordingAndExpectedEventFiredBeforeResetting_fails(self):
        self.startRecordingEvents()
        sut_fires_some()
        self.resetPubSubNotifier()
        self.assertFired("some")

    def test_assertNotFired_whenRecordingAndExpectedEventNotFired_passes(self):
        self.startRecordingEvents()
        sut_fires_another()
        self.assertNotFired("some")

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertNotFired_whenRecordingAndExpectedEventFired_fails(self):
        self.startRecordingEvents()
        sut_fires_another()
        self.assertNotFired("another")

    def test_assertFired_when1FiredAnd1TimesGiven_passes(self):
        self.startRecordingEvents()
        sut_fires_some()
        self.assertFired("some", 1)

    @unittest.expectedFailure # We need unittest2 in Python < 2.7 for this to work
    def test_assertFired_when1FiredAnd2TimesGiven_fails(self):
        self.startRecordingEvents()
        sut_fires_some()
        self.assertFired("some", 2)

    def test_assertFired_when2FiredAnd2TimesGiven_passes(self):
        self.startRecordingEvents()
        sut_fires_some()
        sut_fires_some()
        self.assertFired("some", 2)

    def tearDown(self):
        self.stopRecordingEvents()


if __name__ == "__main__":
    unittest.main()
