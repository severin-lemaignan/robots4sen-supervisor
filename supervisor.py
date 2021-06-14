# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

from csv_logging import create_csv_logger
nb_children_logger = create_csv_logger("logs/nb_children.csv")

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
from activities.listening import activity as listening
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

        self.events_queue = Queue()

        self.cmd_queue = Queue()

        self.bridge = bridge

        self.activity = default_activity.get_activity()
        self.activity.start(self.bridge, self.cmd_queue)

        self._nb_children = 0 # nb of children engaged, as set by the researcher on the ctrl tablet

        self.nb_engaged = 0 # nb of people the robot is currently engaged with
        self.nb_currently_seen = 0 # nb of people current seen by the robot


        # rest_time stores the timestamp at which the last activity stopped
        # used to ensure a 'cool down' period between 2 activities
        self.rest_time = time.time()

    
    isCurrentActivity_changed = Signal(str)
    @Property(str, notify=isCurrentActivity_changed)
    def currentActivity(self):
        return str(self.activity) if (self.activity and self.activity != default_activity.get_activity()) else ""

    @Slot()
    def interruptCurrentActivity(self):

        if self.activity:
            logger.warning("Ctrl tablet requests <%s> to stop" % self.activity)
            self.cmd_queue.put((Event.CTRL_TABLET, INTERRUPT, None))


    nb_children_changed = Signal(int)

    def set_nb_children(self, nb):
        logger.info("# children: %s (was: %s)" % (nb, self._nb_children))
        if nb != self._nb_children:

            if nb == 0:
                self.events_queue.put(Event(Event.NO_ONE_ENGAGED))

            nb_children_logger.info((nb,))
            self._nb_children = nb
            self.nb_children_changed.emit(nb)

    def get_nb_children(self):
        return self._nb_children
    nb_children = Property(int, get_nb_children, set_nb_children, notify=nb_children_changed)

    detected_nb_children_changed = Signal(int)
    @Property(int, notify=detected_nb_children_changed)
    def detected_nb_children(self):
        return len(self.bridge.people.getpeople())

    @Slot()
    def start_single_interaction(self):
        if self.nb_children != 1:
            self.nb_children = 1
        self.events_queue.put(Event(Event.ONE_TO_ONE_ENGAGEMENT, nb_children=1))

    @Slot()
    def start_small_group_interaction(self):
        if self.nb_children < 2 or self.nb_children > 3:
            self.nb_children = 2
        self.events_queue.put(Event(Event.MULTI_ENGAGEMENT, nb_children=self._nb_children))

    @Slot()
    def start_large_group_interaction(self):
        if self.nb_children < 4:
            self.nb_children = 4
        self.events_queue.put(Event(Event.ONE_TO_ONE_ENGAGEMENT, nb_children=self._nb_children))


    def run(self):

        while True:
            self.process_events()
            #logger.debug("%s evt in event queue" % self.events_queue.qsize())
            try:
                evt = self.events_queue.get_nowait()
                logger.debug("Got event: %s" % evt)
            except Empty:
                evt = Event()

            # highest priority: the control tablet requests starting an activity
            if evt.src == Event.CTRL_TABLET and evt.type == Event.ACTIVITY_REQUEST:
                self.startActivity(evt.activity)


            if self.activity is None:
                if evt.type == Event.ACTIVITY_REQUEST:

                        if evt.activity == DEFAULT:
                            self.rest_time = time.time()

                        self.startActivity(evt.activity)
                else: # we have no activity running, but the event was not an activity request. Hopefully the next event will
                    logger.error("No activity running, and the event was not an activity request (was: %s). If this message appears more than once, there is a bug somewhere." % evt)
                    continue


            assert(self.activity is not None)

            if self.activity.type == DEFAULT:

                t = time.time() - self.rest_time
                if t < COOL_DOWN_DURATION:
                    logger.warning("Cool-down period (%.1f/%fs)" % (t, COOL_DOWN_DURATION))

                elif   evt.type == Event.ACTIVITY_REQUEST \
                    or evt.type == Event.ONE_TO_ONE_ENGAGEMENT \
                    or evt.type == Event.MULTI_ENGAGEMENT:

                    self.startActivity(MOODBOARD, evt)


            status = self.activity.tick(evt)

            if status == INTERRUPTED:

                logger.warning("Activity <%s> interrupted" % self.activity)

                # is the activity interrupted due to a request from the child?
                # if so, propose another activity
                if evt.type == Event.INTERRUPTED and evt.src == Event.PEPPER_TABLET:
                    self.startActivity(MOODBOARD, continuation=True)
                else:
                    self.startActivity(DEFAULT)

            elif status == FINISHED:

                logger.info("Activity <%s> completed" % self.activity)

                if self.activity.type == DEFAULT:
                    if self.nb_engaged == 0:
                        # we are coming from default activity: someone pressed the 'waving hand', but wasn't (yet) detected as
                        # engaged. Let's create a temporary 'mock' user
                        logger.info("Initiating interaction without anyone seen yet. Creating a temporary mock user, and hopefully the real user will be detected before the mock user expires.")
                        self.bridge.people.createMockPerson(is_engaged=True, is_temporary=True)

                    self.nb_engaged = 0 # this will re-trigger a interaction event as the current number of engaged children (set ot 0) won't match the detected one


                elif self.activity.type != MOODBOARD:
                    # go back to moodboard to ask whether to continue or final mood
                    self.startActivity(MOODBOARD, continuation=True)

                else: # self.activity.type == MOODBOARD
                    # the moodboard should have put the next activity into the 
                    # cmd_queue, we'll pick it up at the next loop.
                    self.activity = None


    def startActivity(self, activity, *args, **kwargs):
        if activity == DEFAULT:
            self.activity = default_activity.get_activity()
        elif activity == MOODBOARD:
            self.activity = moodboard.get_activity()
        elif activity == STORY:
            self.activity = stories.get_activity()
        elif activity == LISTENING:
            self.activity = listening.get_activity()
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
        elif activity == CUDDLE:
            self.activity = cuddle.get_activity()
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
        if self.nb_currently_seen != nb_currently_seen:
            self.detected_nb_children_changed.emit(nb_currently_seen)
            self.nb_currently_seen = nb_currently_seen

        #logger.debug("Currently seen: %s       Currently engaged: %s (known engaged: %s)" % (nb_currently_seen, nb_currently_engaged, self.nb_engaged))

        # we *only* generate events if:
        #  - the number of currently engaged person goes down to 0
        #  - the number of currently engaged person goes _above_ 0
        #
        #  We do not generate events if eg going from 1 to 2 person engaged

        #if self.nb_engaged != nb_currently_engaged:

        #    # no one engaged anymore, and no-one around
        #    if     nb_currently_engaged == 0 \
        #       and nb_currently_seen == 0:

        #        self.nb_engaged = nb_currently_engaged
        #        self.events_queue.put(Event(Event.NO_ONE_ENGAGED))

        #    elif self.nb_engaged == 0:

        #        # only one person around: one-to-one engagement
        #        if    nb_currently_engaged == 1 \
        #          and nb_currently_seen == 1:

        #              self.nb_engaged = nb_currently_engaged
        #              self.events_queue.put(Event(Event.ONE_TO_ONE_ENGAGEMENT, nb_children=1))

        #        # else, several people around the robot. Even if only
        #        # one is detected as 'engaged', we trigger a group engagement
        #        # event
        #        else:
        #              self.nb_engaged = nb_currently_engaged
        #              self.events_queue.put(Event(Event.MULTI_ENGAGEMENT, nb_children=self.nb_engaged))


        #####################################################################
        ###
        ###   PEPPER TABLET INTERRUPTION REQUESTS

        if self.bridge.tablet.isCancellationRequested():
            self.events_queue.put(Event(Event.INTERRUPTED, src=Event.PEPPER_TABLET))


        #####################################################################
        ###
        ###   ACTIVITY/INTERRUPTION REQUESTS

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)

            logger.debug("GOT A %s CMD: %s (%s)" % (source, cmd, args))

            if cmd == INTERRUPT:
                self.events_queue.put(Event(Event.INTERRUPTED, src=source))
            elif cmd == SOCIAL_GESTURE:
                self.bridge.animate(args)
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
                self.events_queue.put(Event(Event.ACTIVITY_REQUEST, src=source, activity=args))

            else:
                logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd))

        except Empty:
            pass

