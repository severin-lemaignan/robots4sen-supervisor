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
                #ROCK_SCISSOR_PAPER, 
                STORY, 
                ],
            SAD: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE, JOKES],
            #HAPPY: [JOKES, FUN_DANCES, STORY, ROCK_SCISSOR_PAPER],
            HAPPY: [JOKES, FUN_DANCES, STORY, LISTENING],
            CONFUSED: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, CUDDLE, LISTENING],
            ANGRY: [STORY, CALM_DANCES, CALM_MUSIC, RELAX_SOUNDS, LISTENING, CUDDLE],
            }

    def __init__(self):
        super(MoodBoardActivity, self).__init__()

        self.activities_done = []
        self.original_event = Event()
        self.mood = UNKNOWN

    def make_activity_sentences(self, activities, add_all_link=True):

        if len(activities) > 4:
            self.robot.tablet.smallSize()
        else:
            self.robot.tablet.largeSize()

        res = []
        lastverb = None
        for verb, activity, option in [ACTIVITIES_DIALOGUES[a] for a in activities]:
            if not lastverb or lastverb != verb:
                if verb == "listen":
                    lastverb = verb
                    if len(res) == 0:
                        res.append("%s Would you like to listen to %s\\pau=300\\" % (option, activity))
                    else:
                        res.append("%s Or do you feel like listening to %s\\pau=300\\" % (option, activity))
                elif verb == "do":
                    lastverb = verb
                    if len(res) == 0:
                        res.append("%s Do you want me to do %s\\pau=300\\" % (option, activity))
                    else:
                        res.append("%s Or I could do %s\\pau=300\\" % (option, activity))
                else:
                    lastverb = None
                    if len(res) == 0:
                        res.append("%s Do you want me to %s\\pau=300\\" % (option, activity))
                    else:
                        res.append("%s Or I could %s\\pau=300\\" % (option, activity))

            else:
                res.append("%s or %s" % (option, activity))

        if add_all_link:
            res.append('\\option={"id":"%s","img":"images/apps.svg","label": "","footer":true}\\' % ALL)

        return res

    def moods(self):

        options = [
                {"id": ALL, "img": "images/arrow.svg", "label": "", "footer": True}
                ]
        

        self.robot.tablet.clearAll()
        self.robot.tablet.showMoodBoard()
        self.robot.tablet.setOptions(options)

    def is_multiparty(self):
        return self.original_event is not None and self.original_event.nb_children > 3

    def start(self, robot, cmd_queue, event=None, continuation=False):
        """
        continuation: if True, means that mood-board is re-started at the
        end of another activity.
        """
        super(MoodBoardActivity, self).start(robot, cmd_queue)

        if not continuation:

            self.mood = UNKNOWN
            self.activities_done = []
            self.original_event = event

            self._behaviour = self.run()

        else:
            self._behaviour = self.continuation_run()

        logger.warning("Starting a %s interaction" % self.original_event.type)

    def run(self):

        ####################################################################
        ### ASK FOR MOOD

        self.robot.tablet.clearAll()

        if self.is_multiparty(): # skip mood selection
            self.robot.say(get_dialogue("multiparty_prompt")).wait()
            yield RUNNING
            self.mood = UNKNOWN
        else:
            self.moods()
            self.robot.say(get_dialogue("mood_prompt")).wait()
            yield RUNNING


            ####################################################################
            ### WAIT FOR THE CHILD TO CHOOSE AN OPTION

            logger.info("Waiting for mood...")

            while self.response_queue.empty():
                yield RUNNING
            self.mood = self.response_queue.get()["id"].encode()
            if self.mood == ALL:
                self.mood = UNKNOWN

            logger.info("Got mood: %s" % self.mood)
            self.robot.tablet.debug("Got mood: %s" % self.mood)

            ####################################################################
            ### PROMPT 'let do smthg'

            try:
                if self.mood != UNKNOWN:
                    self.robot.say(random.choice(MOODS_FEEDBACK[self.mood])).wait()
                    yield RUNNING
            except KeyError:
                logger.error("Got unexpected mood: %s. Returning to default activity." % self.mood) 
                yield INTERRUPTED

        self.robot.say(get_dialogue("mood_prompt_activities")).wait()
        yield RUNNING

        ####################################################################
        ### OFFER ACTIVITIES BASED ON MOOD

        self.robot.tablet.clearAll()

        if self.mood != UNKNOWN:
            activities = random.sample(self.MOODS_ACTIVITIES[self.mood],
                                       random.randint(2,3))
            sentences = self.make_activity_sentences(activities, add_all_link=True)
        else:
            activities = random.sample(self.MOODS_ACTIVITIES[ALL], 8)
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
        self.cmd_queue.put((Event.PEPPER_TABLET, ACTIVITY, action))

    def continuation_run(self):

        self.robot.tablet.clearAll()
        self.robot.tablet.yesNoBtns()
        self.robot.say(get_dialogue("mood_prompt_continuation")).wait()

        while self.response_queue.empty():
            yield RUNNING
        want_continue = self.response_queue.get()["id"].encode()


        if want_continue == YES:
            logger.debug("Child wants to continue")

            ####################################################################
            ### PROMPT 'let do smthg'

            self.robot.say(get_dialogue("mood_prompt_activities")).wait()
            yield RUNNING

            ####################################################################
            ### OFFER ACTIVITIES BASED ON MOOD

            self.robot.tablet.clearAll()

            if self.mood != UNKNOWN:
                activities = random.sample(self.MOODS_ACTIVITIES[self.mood], random.randint(2,3))
                sentences = self.make_activity_sentences(activities, add_all_link=True)
            else:
                activities = random.sample(self.MOODS_ACTIVITIES[ALL], 8)
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
            self.cmd_queue.put((Event.PEPPER_TABLET, ACTIVITY, action))

        else:
            logger.debug("Child does not want to continue")

            if self.is_multiparty():
                final_mood = UNKNOWN

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
                if final_mood == ALL:
                    final_mood = UNKNOWN

                logger.info("Got final mood: %s" % final_mood)

            mood_logger.info((self.original_event.nb_children, 
                              self.mood, 
                              final_mood, 
                              self.activities_done,
                              FINISHED))

            if final_mood != UNKNOWN:
                self.robot.say(random.choice(FINAL_MOODS_FEEDBACK[final_mood])).wait()
            else:
                self.robot.say(get_dialogue("multiparty_end")).wait()

            self.robot.tablet.clearAll()
            self.cmd_queue.put((Event.PEPPER_TABLET, ACTIVITY, DEFAULT))

    def on_no_one_engaged(self, evt):
        mood_logger.info((self.original_event.nb_children, 
                            self.mood, 
                            UNKNOWN, 
                            self.activities_done,
                            evt.type))

        return super(MoodBoardActivity, self).on_no_one_engaged(evt)

    def on_no_interaction(self, evt):
        mood_logger.info((self.original_event.nb_children, 
                            self.mood, 
                            UNKNOWN, 
                            self.activities_done,
                            evt.type))

        return super(MoodBoardActivity, self).on_no_interaction(evt)

    def on_interrupted(self, evt):
        mood_logger.info((self.original_event.nb_children, 
                            self.mood, 
                            UNKNOWN, 
                            self.activities_done,
                            evt.type))

        return super(MoodBoardActivity, self).on_interrupted(evt)


mood_board_activity = MoodBoardActivity()

def get_activity():
    return mood_board_activity

