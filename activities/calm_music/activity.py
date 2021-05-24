import logging

logger = logging.getLogger("robots.activities.calm_music")

import random

from constants import *
from dialogues import get_dialogue
from events import ActivityEvent

class CalmMusicActivity:

    type = CALM_MUSIC

    def __init__(self):
        pass

    def __str__(self):
        return "Calm music"

    def start(self, robot, cmd_queue):

        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/calm_music")

        self.stop_dance = False

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.behaviour()

    def behaviour(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("calm_music_start")).wait()
        yield RUNNING

        dances = ["robots4sen-brl/calm_music"]

        dance = self.robot.run_behaviour(random.choice(dances))

        while dance.isRunning():
            if self.stop_dance:
                dance.cancel()
                self.stop_dance = False
            yield RUNNING

    def tick(self, evt=None):

        if evt:
            if evt.type == ActivityEvent.INTERRUPTED:
                logger.warning("Activity 'calm music' stopped: interrupt request!");
                self.stop_dance = True
                return STOPPED
            if evt.type == ActivityEvent.NO_ONE_ENGAGED:
                logger.warning("Activity 'calm music' stopped: no one in front of the robot!");
                self.stop_dance = True
                return STOPPED

        try:
            return next(self._behaviour)
        except StopIteration:
            return STOPPED

activity = CalmMusicActivity()

def get_activity():
    return activity
