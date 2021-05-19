from events import ActivityEvent
import logging

logger = logging.getLogger("robots.activities.moodboard")

import json
import time

from constants import *
from dialogues import get_dialogue
from events import ActivityEvent


class MoodBoardActivity:

    def __init__(self):

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

    def start(self, robot, cmd_queue):

        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/mood_board")

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.behaviour()

    def behaviour(self):

        ####################################################################
        ### ASK FOR MOOD

        self.robot.say(get_dialogue("mood_prompt")).wait()
        self.moods()
        yield RUNNING

        ####################################################################
        ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

        logger.info("Waiting for mood...")

        while self.response_queue.empty():
            yield RUNNING
        mood = self.response_queue.get()["id"]

        logger.info("Got mood: %s" % mood)
        self.robot.tablet.debug("Got mood: %s" % mood)
        self.robot.tablet.clearOptions()

        ####################################################################
        ### PROMPT 'let do smthg'

        self.robot.say(get_dialogue("mood_prompt_activities")).wait()
        yield RUNNING

        ####################################################################
        ### OFFER ACTIVITIES BASED ON MOOD

        sentences = [
                'Do you feel like listening to a story?\\option={"id":"%s","img":"images/story.svg","label":"Story"}\\' % STORY,
                'or some music?\\option={"id":"music","img":"images/music.svg","label":"Music"}\\',
                'or a good joke or two?\\option={"id":"%s","img":"images/joke.svg","label":"Jokes"}\\' % JOKES,
                'or maybe I could do a fun dance?\\option={"id":"%s","img":"images/party.svg","label":"Fun dance"}\\' % FUN_DANCES]

        for s in sentences:
            self.robot.say(s).wait()

        yield RUNNING

        ####################################################################
        ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

        logger.info("Waiting for action selection...")

        while self.response_queue.empty(): 
            yield RUNNING
        
        action = self.response_queue.get()["id"]

        logger.info("Got action: %s" % action)
        self.robot.tablet.debug("Got action: %s" % action)

        if action == STORY:
            self.cmd_queue.put((TABLET, ACTIVITY, STORY))
        elif action == JOKES:
            self.cmd_queue.put((TABLET, ACTIVITY, JOKES))
        elif action == FUN_DANCES:
            self.cmd_queue.put((TABLET, ACTIVITY, FUN_DANCES))



    def tick(self, evt=None):

        if evt:
            if evt.type == ActivityEvent.INTERRUPTED:
                logger.warning("Activity mood-board stopped: interrupt request!");
                return STOPPED
            if evt.type == ActivityEvent.NO_ONE_ENGAGED:
                logger.warning("Activity mood-board stopped: no one in front of the robot!");
                return STOPPED

        try:
            return next(self._behaviour)
        except StopIteration:
            return STOPPED

mood_board_activity = MoodBoardActivity()

def get_activity():
    return mood_board_activity

