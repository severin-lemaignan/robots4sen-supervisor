import logging;logger = logging.getLogger("robots.person")

import math
import time

class PersonState(object):
    UNKNOWN = "unknown" # initial, uninitialised state
    LOST = "lost" # when entering 'lost' state, the person is removed
    SEEN = "seen" # has been assigned a 'person id'
    DISAPPEARING = "disappearing" # person not seen, and about to be lost
    ENGAGING = "engaging"
    ENGAGED = "engaged"
    DISENGAGING = "disengaging"

    value = UNKNOWN

    def __init__(self):
        logger.info("Entering state <%s>" % self)

    def step(self,person):
        return self

    def __str__(self):
        return self.value

class UnknownState(PersonState):

    value = PersonState.UNKNOWN

    def step(self, person):

        if person.is_seen():
            return SeenState()

        return self


class SeenState(PersonState):

    value = PersonState.SEEN

    def step(self, person):

        #logger.debug("is close: %s; is looking: %s" % (person.is_close(), person.is_looking()))
        if person.is_close() and person.is_looking():
            return EngagingState()

        if not person.is_seen():
            return DisappearingState()

        return self

class EngagingState(PersonState):

    value = PersonState.ENGAGING

    ENGAGEMENT_MIN_DURATION = 3. #sec -> duration of sustain attention to consider engagement

    def __init__(self):
        super(EngagingState, self).__init__()

        self.start_time = time.time()

    def step(self, person):

        delta = time.time() - self.start_time

        if delta > EngagingState.ENGAGEMENT_MIN_DURATION:
            return EngagedState()
        
        if not person.is_close():
            return SeenState()

        if not person.is_seen():
            return DisappearingState()

        return self

class EngagedState(PersonState):

    value = PersonState.ENGAGED

    def step(self, person):

        if not person.is_close() or not person.is_seen():
            return DisengagingState()

        return self

class DisengagingState(PersonState):

    value = PersonState.DISENGAGING

    DISENGAGEMENT_MIN_DURATION = 3. #sec

    def __init__(self):
        super(DisengagingState, self).__init__()
        
        self.start_time = time.time()

    def step(self, person):

        delta = time.time() - self.start_time

        if delta > DisengagingState.DISENGAGEMENT_MIN_DURATION:
            return SeenState()
        
        if person.is_close() and person.is_seen():
            return EngagedState()

        return self


class DisappearingState(PersonState):

    value = PersonState.DISAPPEARING

    DISAPPEARING_DURATION = 3. #sec

    def __init__(self):
        super(DisappearingState, self).__init__()
        
        self.start_time = time.time()

    def step(self, person):

        delta = time.time() - self.start_time
        #logger.debug("DisengagingState duration: %s" % delta)

        if delta > DisappearingState.DISAPPEARING_DURATION:
            return LostState()
        
        if person.is_seen():
            return SeenState()

        return self

class LostState(PersonState):

    value = PersonState.LOST


class Person():

    ENGAGEMENT_DISTANCE = 2 #m

    # for temporary Persons (usually, temporary mock users),
    # the delay in secs before auto-deleting the person
    SELFDESTRUCTION_DELAY = 20 #s

    # age groups
    AGE_UNKNOWN = "unknown"
    ADULT = "adult"
    CHILD = "child"

    def __init__(self, id, 
                 state = None,
                 location = [0., 0., 0.], 
                 selfdestruct=False):

        self.state = state if state is not None else UnknownState()

        self.person_id = id
        self.user_id = 0
        self.location = location
        self.world_location = [0., 0., 0.]

        self.created_at = time.time()
        self.selfdestruct = selfdestruct

        self.age = self.AGE_UNKNOWN

        self.looking_at_robot = 0.

    def __str__(self):
        return "<Person %s>" % self.person_id

    def is_mock_person(self):
        return self.person_id < 0


    def distance(self):
        """ Returns the 2D (x,y) distance to the robot (z ignored)
        """
        x,y,_=self.location
        return math.sqrt(x*x+y*y)

    def distance_to(self, x, y, z):
        """ Returns the 2D (x,y) distance between the person and a 2d point (z ignored)
        """
        x1,y1,_=self.location
        return math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))

    def is_close(self):
        #logger.debug("Distance to robot: %.2fm" % self.distance())
        return self.distance() < self.ENGAGEMENT_DISTANCE

    def is_looking(self):
        return self.is_mock_person() or self.looking_at_robot > 0.5

    def is_seen(self):
        if self.is_mock_person():
            return self.location[0] > 0 # mock person in front of the robot
        else:
            return bool(self.location[0]) and bool(self.location[1])

    def is_engaged(self):
        return self.state.value in [PersonState.ENGAGED, PersonState.DISENGAGING]

    def update(self):
        """
        Returns: True if the person's state has not changed, False otherwise.
        """

        oldstate = self.state

        if     self.selfdestruct \
           and time.time() - self.created_at > Person.SELFDESTRUCTION_DELAY:
               self.state = LostState()

        else:
               self.state = self.state.step(self)

        return oldstate == self.state
