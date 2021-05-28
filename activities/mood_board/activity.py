import logging

from csv_logging import create_csv_logger

logger = logging.getLogger("robots.activities.moodboard")
mood_logger = create_csv_logger("logs/moods.csv") 

import json
import time
import random

from constants import *
from dialogues import *
from events import Event

from activities.activity import Activity, action_logger

class MoodBoardActivity(Activity):

    type = MOODBOARD

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
            SAD: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE, JOKES],
            HAPPY: [JOKES, FUN_DANCES, STORY, ROCK_SCISSOR_PAPER],
            CONFUSED: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, CUDDLE, LISTENING],
            ANGRY: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE],
            }

    def __init__(self):
        super(MoodBoardActivity, self).__init__()

        self.activities_done = []

    def make_activity_sentences(self, activities, add_all_link=True):
        res = []
        lastverb = None
        for verb, activity, option in [ACTIVITIES_DIALOGUES[a] for a in activities]:
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
                {"id": ALL, "img": "images/arrow.svg", "label": "Skip", "footer": True}
                ]
        

        self.robot.tablet.clearAll()
        self.robot.tablet.showMoodBoard()
        self.robot.tablet.setOptions(options)

    def start(self, robot, cmd_queue, continuation=False):
        """
        continuation: if True, means that mood-board is re-started at the
        end of another activity.
        """
        super(MoodBoardActivity, self).start(robot, cmd_queue)

        if not continuation:

            self.mood = None
            self.activities_done = []

            self._behaviour = self.run()

        else:
            self._behaviour = self.continuation_run()

    def run(self):

        ####################################################################
        ### ASK FOR MOOD

        self.robot.tablet.clearAll()
        self.moods()
        self.robot.say(get_dialogue("mood_prompt")).wait()
        yield RUNNING

        ####################################################################
        ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

        logger.info("Waiting for mood...")

        while self.response_queue.empty():
            yield RUNNING
        self.mood = self.response_queue.get()["id"].encode()

        logger.info("Got mood: %s" % self.mood)
        self.robot.tablet.debug("Got mood: %s" % self.mood)

        ####################################################################
        ### PROMPT 'let do smthg'

        if self.mood != ALL:
            self.robot.say(random.choice(MOODS_FEEDBACK[self.mood])).wait()
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

        self.robot.tablet.clearAll()

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

    def continuation_run(self):

        self.robot.tablet.clearAll()
        self.robot.tablet.yesNoBtns()
        self.robot.say(get_dialogue("mood_prompt_continuation")).wait()

        while self.response_queue.empty():
            yield RUNNING
        want_continue = self.response_queue.get()["id"].encode()


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

            self.robot.tablet.clearAll()

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
            self.robot.tablet.clearAll()
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

            if final_mood != ALL:
                self.robot.say(random.choice(FINAL_MOODS_FEEDBACK[self.mood])).wait()

            self.robot.tablet.clearAll()

mood_board_activity = MoodBoardActivity()

def get_activity():
    return mood_board_activity

