# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

import time
from Queue import Queue, Empty

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property


from constants import *

from events import Event

###########################################
# ACTIVITIES
from activities.default import activity as default_activity
from activities.mood_board import activity as moodboard
from activities.stories import activity as stories
from activities.jokes import activity as jokes
from activities.fun_dances import activity as fun_dances
from activities.calm_music import activity as calm_music
from activities.calm_dances import activity as calm_dances
from activities.relax_sounds import activity as relax_sounds
from activities.cuddle import activity as cuddle

###########################################

TICK_PERIOD = 0.05 #sec
COOL_DOWN_DURATION = 1 #sec

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        self.activity = default_activity.get_activity()
        self.activity.start(self.bridge, self.cmd_queue)

        self.nb_engaged = 0 # nb of people the robot is currently engaged with

        # rest_time stores the timestamp at which the last activity stopped
        # used to ensure a 'cool down' period between 2 activities
        self.rest_time = time.time()

    
    isCurrentActivity_changed = Signal(str)
    @Property(str, notify=isCurrentActivity_changed)
    def currentActivity(self):
        return str(self.activity) if self.activity else ""

    @Slot()
    def interruptCurrentActivity(self):

        if self.activity:
            logger.warning("Ctrl tablet requests <%s> to stop" % self.activity)
            self.request_interrupt = True


    def run(self):

        has_completed_mood_continuation = False

        while True:
            evt = self.process_events()

            if self.activity.type == DEFAULT:

                t = time.time() - self.rest_time
                if t < COOL_DOWN_DURATION:
                    logger.warning("Cool-down period (%.1f/%fs)" % (t, COOL_DOWN_DURATION))

                elif    evt.type == Event.ACTIVITY_REQUEST \
                     or evt.type == Event.ONE_TO_ONE_ENGAGEMENT \
                     or evt.type == Event.MULTI_ENGAGEMENT:

                    self.startActivity(MOODBOARD, evt)


            status = self.activity.tick(evt)

            if status == STOPPED:

                logger.info("Activity <%s> completed" % self.activity)

                if self.activity.type != MOODBOARD:
                    # go back to moodboard to ask whether to continue or final mood
                    self.startActivity(MOODBOARD, continuation=True)

                else: # self.activity.type == MOODBOARD

                    if evt.type == Event.ACTIVITY_REQUEST:
                        if evt.activity == DEFAULT:
                            self.rest_time = time.time()

                        self.startActivity(evt.activity)


    def startActivity(self, activity, *args, **kwargs):
        if activity == DEFAULT:
            self.activity = default_activity.get_activity()
        elif activity == MOODBOARD:
            self.activity = moodboard.get_activity()
        elif activity == STORY:
            self.activity = stories.get_activity()
        elif activity == JOKES:
            self.activity = jokes.get_activity()
        elif activity == FUN_DANCES:
            self.activity = fun_dances.get_activity()
        elif activity == CALM_MUSIC:
            self.activity = calm_music.get_activity()
        elif activity == RELAX_SOUNDS:
            self.activity = relax_sounds.get_activity()
        elif activity == CALM_DANCES:
            self.activity = calm_dances.get_activity()
        else:
            logger.error("Unknown activity <%s>. Falling back to DEFAULT" % activity)
            self.activity = default_activity.get_activity()
            return

        logger.info("Activity <%s> starting" % self.activity)


        self.activity.start(self.bridge, self.cmd_queue, *args, **kwargs)

        self.isCurrentActivity_changed.emit(str(self.activity))


    def process_events(self):


        ####################################################################
        ###
        ###  ENGAGEMENT/DISENGAGEMENT EVENTS

        nb_currently_engaged = len(self.bridge.people.getengagedpeople())
        nb_currently_seen = len(self.bridge.people.getpeople())

        # we *only* generate events if:
        #  - the number of currently engaged person goes down to 0
        #  - the number of currently engaged person goes _above_ 0
        #
        #  We do not generate events if eg going from 1 to 2 person engaged

        if self.nb_engaged != nb_currently_engaged:

            # no one engaged anymore
            if nb_currently_engaged == 0:
                self.nb_engaged = nb_currently_engaged
                return Event(Event.NO_ONE_ENGAGED)

            if self.nb_engaged == 0:

                # only one person around: one-to-one engagement
                if    nb_currently_engaged == 1 \
                  and nb_currently_seen == 1:
                      self.nb_engaged = nb_currently_engaged
                      return Event(Event.ONE_TO_ONE_ENGAGEMENT, nb_children=1)

                # else, several people around the robot. Even if only
                # one is detected as 'engaged', we trigger a group engagement
                # event
                else:
                      self.nb_engaged = nb_currently_engaged
                      return Event(Event.MULTI_ENGAGEMENT, nb_children=self.nb_engaged)


        #####################################################################
        ###
        ###   CTRL TABLET INTERRUPTION REQUESTS

        if self.bridge.tablet.isCancellationRequested():
            return Event(Event.INTERRUPTED, src=Event.CTRL_TABLET)


        #####################################################################
        ###
        ###   ACTIVITY/INTERRUPTION REQUESTS

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)
        except Empty:
            return Event()

        logger.debug("GOT A %s CMD: %s (%s)" % (source, cmd, args))

        if cmd == INTERRUPT:
            return Event(Event.INTERRUPTED, src=source)
        #elif cmd == SOCIAL_GESTURE:
        #    self.bridge.animate(args)
        #elif cmd == BEHAVIOUR:
        #    self.bridge.run_behaviour(args)
        #elif cmd == LOOK_AT:
        #    self.bridge.lookAt(*args)
        #elif cmd == TRACK:
        #    if not args:
        #        self.bridge.stop_tracking()
        #    else:
        #        self.bridge.track(args)
        elif cmd == ACTIVITY:
            return Event(Event.ACTIVITY_REQUEST, src=source, activity=args)

        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd))


