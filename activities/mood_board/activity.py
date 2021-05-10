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

    def moods(self):

        options = [
                {"id": "partymood", "img": "images/partymood.svg", "label": "Party!"},
                {"id": "happy", "img": "images/happy.svg", "label": "Happy"},
                {"id": "confused", "img": "images/confused.svg", "label": "Not sure"},
                {"id": "tired", "img": "images/tired.svg", "label": "Tired"},
                {"id": "sad", "img": "images/sad.svg", "label": "Sad"},
                {"id": "angry", "img": "images/angry.svg", "label": "Angry"},
                {"id": "skip", "img": "images/flash.svg", "label": "Skip", "footer": True}
                ]

        self.robot.tablet.clearOptions()
        self.robot.tablet.setOptions(options)

    def start(self, robot, mood=None):

        self.robot = robot

        self.status = RUNNING
        self.robot.tablet.debug("activity/mood_board")

        self.robot.say(get_dialogue("mood_prompt")).wait()
        self.moods()
        logger.info("[BLOCKING] Waiting for mood...")
        mood = self.robot.tablet.response_queue.get()
        logger.info("Got mood: %s" % mood)
        self.robot.tablet.debug("Got mood: %s" % mood)

        self.robot.tablet.clearOptions()


        sentences = [
                'Do you feel like listening to music?\\option={"id":"music","img":"images/music.svg","label":"Music"}\\',
                'or maybe I could do a fun dance?\\option={"id":"fun_dance","img":"images/party.svg","label":"Fun dance"}\\']

        for s in sentences:
            self.robot.say(s).wait()

        # blocking call: we wait until the user chose what option he/she wants
        logger.info("[BLOCKING] Waiting for action selection...")
        action = self.robot.tablet.response_queue.get()

        self.status = STOPPED

    def tick(self):

        return self.status


mood_board_activity = MoodBoardActivity()

def get_activity():
    return mood_board_activity

