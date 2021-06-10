import logging

logger = logging.getLogger("robots.activities.default")

import json
import time

from constants import *
from events import Event

from activities.activity import Activity

class DefaultActivity(Activity):

    type = DEFAULT

    def __init__(self):
        super(DefaultActivity, self).__init__()

    def start(self, robot, cmd_queue):
        super(DefaultActivity, self).start(robot, cmd_queue)

        # display the waving hand
        self.robot.tablet.clearAll()
        self.robot.tablet.default()

    def run(self):

        ####################################################################
        ### WAIT FOR THE CHILD TO CLICK ON THE WAVING HAND

        while self.robot.tablet.response_queue.empty():
            yield RUNNING

        msg = self.robot.tablet.response_queue.get()
        if msg["id"] != "default":
            logger.error("[EE] Did not get 'default' as option choice while in default activity. The tablet response queue contains old values!")
            logger.error("Got: %s" % msg)


        self.cmd_queue.put((Event.PEPPER_TABLET, MOODBOARD, None))


default_activity = DefaultActivity()

def get_activity():
    return default_activity

