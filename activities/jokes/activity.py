import logging

logger = logging.getLogger("robots.activities.jokes")

import random

from constants import *
from dialogues import get_dialogue
from events import ActivityEvent

JOKES = [
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
        ]

class JokesActivity:

    def __init__(self):
        pass

    def __str__(self):
        return "Jokes"

    def start(self, robot, cmd_queue):

        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/jokes")

        self.jokes = random.sample(JOKES, random.randint(2,5))

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.behaviour()

    def behaviour(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("jokes_start")).wait()
        yield RUNNING

        while self.jokes:
            joke = self.jokes.pop()
            self.robot.say(joke).wait()
            yield RUNNING

        self.robot.say(get_dialogue("jokes_end")).wait()

    def tick(self, evt=None):

        if evt:
            if evt.type == ActivityEvent.INTERRUPTED:
                logger.warning("Activity 'jokes' stopped: interrupt request!");
                return STOPPED
            if evt.type == ActivityEvent.NO_ONE_ENGAGED:
                logger.warning("Activity 'jokes' stopped: no one in front of the robot!");
                self.robot.say(get_dialogue("jokes_no_one_left")).wait()
                return STOPPED

        try:
            return next(self._behaviour)
        except StopIteration:
            return STOPPED

activity = JokesActivity()

def get_activity():
    return activity

