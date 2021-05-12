# utf-8

from events import ActivityEvent
import logging;logger = logging.getLogger("robots.supervisor")

from csv_logging import create_csv_logger

action_logger = create_csv_logger("logs/actions.csv") 

from Queue import Queue, Empty

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property


from constants import *

from events import ActivityEvent

###########################################
# ACTIVITIES
from activities.default import activity as default_activity
from activities.mood_board import activity as moodboard
from activities.stories import activity as stories

###########################################

TICK_PERIOD = 0.05 #sec

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        self.activity = None
        self.request_interrupt = False
    
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

                if self.activity == default_activity.get_activity():
                    if len(self.bridge.people.getengagedpeople()) > 0:
                        logger.info("Someone is engaging! Start moodboard")
                        self.activity = moodboard.get_activity()
                        self.activity.start(self.bridge, self.cmd_queue)
                        

                evt = None
                if self.request_interrupt:
                    evt = ActivityEvent(ActivityEvent.INTERRUPTED)
                if len(self.bridge.people.getengagedpeople()) == 0:
                    evt = ActivityEvent(ActivityEvent.NO_ONE_ENGAGED)


                status = self.activity.tick(evt)

                if status == STOPPED:
                    logger.info("Activity <%s> completed" % self.activity)
                    action_logger.info((self.activity, status))
                    self.activity = None
                    self.request_interrupt = False
                    self.isCurrentActivity_changed.emit(str(self.activity))

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

    def startActivity(self, activity):
        self.activity = activity
        logger.info("Activity <%s> starting" % self.activity)
        self.activity.start(self.bridge, self.cmd_queue)
        action_logger.info((self.activity, RUNNING))
        self.isCurrentActivity_changed.emit(str(self.activity))


    def process_queue(self):

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)
        except Empty:
            return

        logger.debug("GOT A %s CMD: %s (%s)" % (source, cmd, args))
        action_logger.info((source, cmd, args))
        
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

        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 

