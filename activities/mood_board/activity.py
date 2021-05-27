from events import ActivityEvent
import logging

from csv_logging import create_csv_logger

logger = logging.getLogger("robots.activities.moodboard")
mood_logger = create_csv_logger("logs/moods.csv") 

import json
import time
import random

from constants import *
from dialogues import get_dialogue
from events import ActivityEvent

from supervisor import action_logger

class MoodBoardActivity:

    type = MOODBOARD

    ACTIVITIES = {
            CALM_DANCES: ['do', 'a dance?', '\\option={"id":"%s","img":"images/calm_dance.svg","label":"Calm dance"}\\' % CALM_DANCES],
            CALM_MUSIC: ['listen', 'some music?', '\\option={"id":"%s","img":"images/music.svg","label":"Music"}\\' % CALM_MUSIC],
            CUDDLE: ['do', 'a cuddle?', '\\option={"id":"%s","img":"images/cuddle.svg","label":"Cuddle"}\\' % CUDDLE],
            FUN_DANCES: ['do', 'a fun dance?', '\\option={"id":"%s","img":"images/party.svg","label":"Fun dance"}\\' % FUN_DANCES],
            JOKES: ['listen', 'a good joke or two?', '\\option={"id":"%s","img":"images/joke.svg","label":"Jokes"}\\' % JOKES],
            LISTENING: ['other', 'simply listen to you?', '\\option={"id":"%s","img":"images/speak.svg","label":"Talking"}\\' % LISTENING],
            RELAX_SOUNDS: ['listen', 'relaxing sounds?', '\\option={"id":"%s","img":"images/relax.svg","label":"Sounds"}\\' % RELAX_SOUNDS],
            ROCK_SCISSOR_PAPER: ['play', 'rock paper scissors?', '\\option={"id":"%s","img":"images/scissors.svg","label":"Rock Paper Scissors"}\\' % ROCK_SCISSOR_PAPER],
            STORY: ['listen', 'a story?', '\\option={"id":"%s","img":"images/story.svg","label":"Story"}\\' % STORY],
            }

    MOODS_FEEDBACK = {
            PARTYMOOD: ["Cool!", "Full of energy!", "Good, I like that!"],
            HAPPY: ["Good to hear!", "Glad you feel good!", "Cool!", "Nice!"],
            CONFUSED: ["Not too sure? Let see.","A bit lost? Let see.", "That's ok.", "A bit confused? That's ok.", "Let see what we can do."],
            TIRED: ["A bit tired? Ok, let see.", "Ok, that's fine.", "Not too much energy? no worries.", "Ok, that's fine to be tired sometimes!"],
            SAD: ["Oh, sorry to hear that you feel sad", "You feel sad? Let see what we can do.", "That's ok, let see.", "Ok, thank you for letting me know."],
            ANGRY: ["Oh! You feel angry? Let see.", "You feel angry? Ok, thanks for telling me", "Ok, let see if we can calm down a little then", "That's ok to feel angry. Let see what we can do."],
            }


    MOODS_ACTIVITIES = {
            ALL: [
                CALM_DANCES, 
                CALM_MUSIC, 
                CUDDLE,
                FUN_DANCES, 
                JOKES, 
                LISTENING, 
                RELAX_SOUNDS, 
                ROCK_SCISSOR_PAPER, 
                STORY, 
                ],
            PARTYMOOD: [JOKES, FUN_DANCES, ROCK_SCISSOR_PAPER],
            HAPPY: [JOKES, FUN_DANCES, STORY, ROCK_SCISSOR_PAPER],
            CONFUSED: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, CUDDLE],
            TIRED: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, CUDDLE, FUN_DANCES],
            SAD: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE, JOKES],
            ANGRY: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE],
            }

    def __init__(self):

        self.progress = 0

        self.current_speech_action = None

        self.activities_done = []


    def __str__(self):
        return "Mood board"

    def make_activity_sentences(self, activities, add_all_link=True):
        res = []
        lastverb = None
        for verb, activity, option in [self.ACTIVITIES[a] for a in activities]:
            if not lastverb or lastverb != verb:
                if verb == "listen":
                    lastverb = verb
                    if len(res) == 0:
                        res.append("%s Would you like to listen to %s" % (option, activity))
                    else:
                        res.append("%s Or do you feel like listening to %s" % (option, activity))
                elif verb == "do":
                    lastverb = verb
                    if len(res) == 0:
                        res.append("%s Do you want me to do %s" % (option, activity))
                    else:
                        res.append("%s Or I could do %s" % (option, activity))
                else:
                    lastverb = None
                    if len(res) == 0:
                        res.append("%s Do you want me to %s" % (option, activity))
                    else:
                        res.append("%s Or I could %s" % (option, activity))

            else:
                res.append("%s or %s" % (option, activity))

        if add_all_link:
            res.append('\\option={"id":"%s","img":"images/again.svg","label": "All","footer":true}\\' % ALL)

        return res

    def moods(self):

        options = [
                {"id": PARTYMOOD, "img": "images/partymood.svg", "label": "Party!"},
                {"id": HAPPY, "img": "images/happy.svg", "label": "Happy"},
                {"id": CONFUSED, "img": "images/confused.svg", "label": "Not sure"},
                {"id": TIRED, "img": "images/tired.svg", "label": "Tired"},
                {"id": SAD, "img": "images/sad.svg", "label": "Sad"},
                {"id": ANGRY, "img": "images/angry.svg", "label": "Angry"},
                {"id": ALL, "img": "images/arrow.svg", "label": "Skip", "footer": True}
                ]
        

        self.robot.tablet.clearOptions()
        self.robot.tablet.setOptions(options)

    def start(self, robot, cmd_queue, continuation=False):
        """
        continuation: if True, means that mood-board is re-started at the
        end of another activity.
        """

        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/mood_board")

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        if not continuation:

            self.mood = None
            self.activities_done = []

            self._behaviour = self.behaviour()

        else:
            self._behaviour = self.continuation_behaviour()

    def behaviour(self):

        ####################################################################
        ### ASK FOR MOOD

        self.robot.tablet.clearAll()
        self.robot.say(get_dialogue("mood_prompt")).wait()
        self.moods()
        yield RUNNING

        ####################################################################
        ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

        logger.info("Waiting for mood...")

        while self.response_queue.empty():
            yield RUNNING
        self.mood = self.response_queue.get()["id"].encode()

        logger.info("Got mood: %s" % self.mood)
        self.robot.tablet.debug("Got mood: %s" % self.mood)
        self.robot.tablet.clearAll()

        ####################################################################
        ### PROMPT 'let do smthg'

        if self.mood != ALL:
            self.robot.say(random.choice(self.MOODS_FEEDBACK[self.mood])).wait()
            yield RUNNING

        self.robot.say(get_dialogue("mood_prompt_activities")).wait()
        yield RUNNING

        ####################################################################
        ### OFFER ACTIVITIES BASED ON MOOD

        if self.mood != ALL:
            activities = random.sample(self.MOODS_ACTIVITIES[self.mood],
                                       random.randint(2,3))
            sentences = self.make_activity_sentences(activities, add_all_link=True)
        else:
            activities = random.sample(self.MOODS_ACTIVITIES[self.mood], 8)
            sentences = self.make_activity_sentences(activities, add_all_link=False)

        while True:
            logger.info("Offering the following activities: %s" % activities)

            for s in sentences:
                self.robot.say(s).wait()
                if not self.response_queue.empty(): 
                    break
                yield RUNNING


            ####################################################################
            ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

            logger.info("Waiting for action selection...")

            while self.response_queue.empty(): 
                yield RUNNING
            
            action = self.response_queue.get()["id"]

            logger.info("Got action: %s" % action)
            self.robot.tablet.debug("Got action: %s" % action)

            if action == ALL:
                self.robot.tablet.clearAll()
                self.robot.say(get_dialogue("mood_all_activities")).wait()
                yield RUNNING
                activities = random.sample(self.MOODS_ACTIVITIES[ALL], 8)
                sentences = self.make_activity_sentences(activities, add_all_link=False)
            else:
                break

        self.activities_done.append(action)
        action_logger.info((action, self.mood))
        self.cmd_queue.put((TABLET, ACTIVITY, action))

    def continuation_behaviour(self):

        self.robot.tablet.clearAll()
        self.robot.tablet.yesNoBtns()
        self.robot.say(get_dialogue("mood_prompt_continuation")).wait()

        while self.response_queue.empty():
            yield RUNNING
        want_continue = self.response_queue.get()["id"].encode()

        self.robot.tablet.clearAll()

        if want_continue == YES:

            ####################################################################
            ### PROMPT 'let do smthg'

            self.robot.say(get_dialogue("mood_prompt_activities")).wait()
            yield RUNNING

            ####################################################################
            ### OFFER ACTIVITIES BASED ON MOOD

            if self.mood != ALL:
                activities = random.sample(self.MOODS_ACTIVITIES[self.mood], random.randint(2,3))
                sentences = self.make_activity_sentences(activities, add_all_link=True)
            else:
                activities = random.sample(self.MOODS_ACTIVITIES[self.mood], 8)
                sentences = self.make_activity_sentences(activities, add_all_link=False)

            while True:
                logger.info("Offering the following activities: %s" % activities)

                for s in sentences:
                    self.robot.say(s).wait()
                    if not self.response_queue.empty(): 
                        break
                    yield RUNNING


                ####################################################################
                ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

                logger.info("Waiting for action selection...")

                while self.response_queue.empty(): 
                    yield RUNNING
                
                action = self.response_queue.get()["id"]

                logger.info("Got action: %s" % action)
                self.robot.tablet.debug("Got action: %s" % action)

                if action == ALL:
                    self.robot.tablet.clearAll()
                    self.robot.say(get_dialogue("mood_all_activities")).wait()
                    yield RUNNING
                    activities = random.sample(self.MOODS_ACTIVITIES[ALL], 8)
                    sentences = self.make_activity_sentences(activities, add_all_link=False)
                else:
                    break


            self.activities_done.append(action)
            self.cmd_queue.put((TABLET, ACTIVITY, action))

        else:

            ####################################################################
            ### ASK FOR MOOD

            self.robot.say(get_dialogue("mood_end")).wait()
            self.moods()
            yield RUNNING

            ####################################################################
            ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

            logger.info("Waiting for final mood...")

            while self.response_queue.empty():
                yield RUNNING

            final_mood = self.response_queue.get()["id"].encode()

            logger.info("Got final mood: %s" % final_mood)
            mood_logger.info((self.mood, final_mood, self.activities_done))
            self.robot.tablet.clearAll()


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

