import logging
logger = logging.getLogger("robots.activities.jokes")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

JOKES_LIST = [
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "Why did the teddy bear say no to dessert?\\pau=1700\\^startTag(down)Because she was stuffed.",
            "What did the left eye say to the right eye?\\pau=1600\\Between us, something smells!",
            "What is brown, hairy and wears sunglasses?\\pau=1400\\A coconut on vacation.",
            "When you look for something, why is it always in the last place you look?\\pau=1400\\Because when you find it, you stop looking.",
            "Why did the kid cross the playground?\\pau=1400\\To get to the other slide.",
            "Why was 6 afraid of 7?\\pau=1800\\Because 7 8 9.",
            "What is a witch's favorite subject in school?\\pau=1300\\Spelling!",
        ]

class JokesActivity(Activity):

    type = JOKES

    def __init__(self):
        super(JokesActivity, self).__init__()

    def start(self, robot, cmd_queue):
        super(JokesActivity, self).start(robot, cmd_queue)

        self.jokes = random.sample(JOKES_LIST, random.randint(2,5))

    def run(self):

        self.robot.tablet.clearAll()
        self.robot.say(get_dialogue("jokes_start")).wait()
        yield RUNNING

        self.robot.tablet.addCancelBtn()

        while self.jokes:
            joke = self.jokes.pop()
            self.robot.say(joke).wait()
            yield RUNNING

            if self.jokes:
                self.robot.say(get_dialogue("jokes_inbetween")).wait()
                yield RUNNING

        self.robot.say(get_dialogue("jokes_end")).wait()

    def on_no_one_engaged(self, evt):
        self.robot.say(get_dialogue("jokes_no_one_left")).wait()
        return super(JokesActivity, self).on_no_one_engaged(evt)

activity = JokesActivity()

def get_activity():
    return activity

