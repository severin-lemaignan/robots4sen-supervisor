import logging

logger = logging.getLogger("robots.activities.moodboard")

import json
import time

from constants import *
from dialogues import get_dialogue


class MoodBoardActivity:

    def __init__(self):

        self.status = STOPPED
        self.progress = 0

        self.current_speech_action = None


    def __str__(self):
        return "Mood board"

    def start(self, robot, mood=None):

        self.robot = robot

        self.status = RUNNING
        self.robot.say(get_dialogue("mood_prompt")).wait()
        time.sleep(1)
        self.robot.tablet.clearOptions()
        self.robot.tablet.debug("activity/mood_board")


        sentences = [
                'Do you feel like listening to music?\\option={"id":"music","img":"images/music.svg","label":"Music"}\\',
                'or maybe I could do a fun dance?\\option={"id":"fun_dance","img":"images/saxophone.svg","label":"Fun dance"}\\']

        for s in sentences:
            self.robot.say(s).wait()

        # blocking call: we wait until the user chose what option he/she wants
        action = self.robot.tablet.response_queue.get()

        self.status = STOPPED

    def tick(self):

        return self.status


mood_board_activity = MoodBoardActivity()

def get_activity():
    return mood_board_activity

