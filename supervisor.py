# utf-8

from events import ActivityEvent
import logging;logger = logging.getLogger("robots.supervisor")

from csv_logging import create_csv_logger

action_logger = create_csv_logger("logs/actions.csv") 

import time
from Queue import Queue, Empty

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property


from constants import *

from events import ActivityEvent

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

###########################################

TICK_PERIOD = 0.05 #sec
COOL_DOWN_DURATION = 5 #sec

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        self.activity = None
        self.request_interrupt = False

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

        while True:
            self.process_queue()
            
            #logger.debug("%s people detected" % len(self.bridge.people.getpeople()))
            #logger.debug("%s people engaged" % len(self.bridge.people.getengagedpeople()))

            if self.activity:

                if self.activity.type == DEFAULT:
                    t = time.time() - self.rest_time
                    if t < COOL_DOWN_DURATION:
                        logger.warning("Cool-down period (%.1f/%fs)" % (t, COOL_DOWN_DURATION))
                        continue

                    if len(self.bridge.people.getengagedpeople()) > 0:
                        logger.warning("Someone is engaging! Start moodboard")
                        self.startActivity(moodboard.get_activity())

                evt = None
                if self.activity.type != DEFAULT:
                    if self.request_interrupt or self.bridge.tablet.isCancellationRequested():

                        src = ActivityEvent.CTRL_TABLET if self.request_interrupt else ActivityEvent.PEPPER_TABLET
                        evt = ActivityEvent(ActivityEvent.INTERRUPTED,src)
                        action_logger.info((self.activity.type, str(evt)))

                    if len(self.bridge.people.getengagedpeople()) == 0:
                        evt = ActivityEvent(ActivityEvent.NO_ONE_ENGAGED)
                        action_logger.info((self.activity.type, str(evt)))


                status = self.activity.tick(evt)

                if status == STOPPED:
                    logger.info("Activity <%s> completed" % self.activity)
                    action_logger.info((self.activity.type, status))

                    # implement logic to either:
                    #  - go back to moodboard and either do another activity or ask final mood
                    #  - or go to rest (default waving hand)
                    if self.activity == moodboard.get_activity():
                        self.activity = None
                        self.request_interrupt = False
                        self.isCurrentActivity_changed.emit(None)
                        self.rest_time = time.time()
                    else:
                        logger.warning("Returning to moodboard")
                        self.startActivity(moodboard.get_activity(), True) # continuation = True

            # if no active activity, and no activity was enqueue, fall back to the
            # default activity (eg, the waving hand)
            else:
                if self.bridge.tablet.isConnected():
                    logger.info("Starting default activity")
                    self.activity = default_activity.get_activity()
                    self.activity.start(self.bridge, self.cmd_queue)
                else:
                    pass
                    #logger.warning("Waiting for Pepper's tablet to be connected")

    def startActivity(self, activity, *args):
        self.activity = activity
        logger.info("Activity <%s> starting" % self.activity)

        if args:
            self.activity.start(self.bridge, self.cmd_queue, *args)
        else:
            self.activity.start(self.bridge, self.cmd_queue)

        action_logger.info((self.activity.type, RUNNING))
        self.isCurrentActivity_changed.emit(str(self.activity))


    def process_queue(self):

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)
        except Empty:
            return

        logger.debug("GOT A %s CMD: %s (%s)" % (source, cmd, args))
        
        if cmd == INTERRUPT:
            if self.activity:
                self.request_interrupt = True
        elif cmd == SOCIAL_GESTURE:
            self.bridge.animate(args)
        elif cmd == BEHAVIOUR:
            self.bridge.run_behaviour(args)
        elif cmd == LOOK_AT:
            self.bridge.lookAt(*args)
        elif cmd == TRACK:
            if not args:
                self.bridge.stop_tracking()
            else:
                self.bridge.track(args)
        elif cmd == MOODBOARD:
            self.startActivity(moodboard.get_activity())

        elif cmd == ACTIVITY:
                if args == STORY:
                    self.startActivity(stories.get_activity())
                elif args == JOKES:
                    self.startActivity(jokes.get_activity())
                elif args == FUN_DANCES:
                    self.startActivity(fun_dances.get_activity())
                elif args == CALM_MUSIC:
                    self.startActivity(calm_music.get_activity())
                elif args == RELAX_SOUNDS:
                    self.startActivity(relax_sounds.get_activity())
                elif args == CALM_DANCES:
                    self.startActivity(calm_dances.get_activity())


        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 

