import logging

logger = logging.getLogger("robots.activities.default")

import json
import time

from constants import *


class DefaultActivity:

    def __init__(self):
        pass

    def __str__(self):
        return "Default"

    def start(self, robot, cmd_queue):

        self.robot = robot
        self.cmd_queue = cmd_queue

        self.robot.tablet.debug("activity/default")

        # display the waving hand
        self.robot.tablet.clearAll()
        self.robot.tablet.default()

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.behaviour()

    def behaviour(self):

        ####################################################################
        ### WAIT FOR THE CHILD TO CLICK ON THE WAVING HAND

        while self.robot.tablet.response_queue.empty():
            yield RUNNING

        if self.robot.tablet.response_queue.get()["id"] != "default":
            logger.error("[EE] Did not get 'default' as option choice while in default activity. The tablet response queue contains old values!")


        self.cmd_queue.put((TABLET, MOODBOARD, None))

    def tick(self, evt=None):
        try:
            return next(self._behaviour)
        except StopIteration:
            return STOPPED

default_activity = DefaultActivity()

def get_activity():
    return default_activity

