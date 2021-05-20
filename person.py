import logging;logger = logging.getLogger("robots.person")

import math
import time

class PersonState:
    UNKNOWN = "unknown"
    SEEN = "seen" # has been assigned a 'person id'
    IDENTIFIED = "identified" # has been assigned a 'user id'
    ENGAGING = "engaging"
    ENGAGED = "engaged"
    DISENGAGING = "disengaging"

class Person():

    ENGAGEMENT_DISTANCE = 2 #m
    ENGAGEMENT_MIN_DURATION = 4. #sec -> duration of sustain attention to consider engagement
    DISENGAGEMENT_MIN_DURATION = 5. #sec


    def __init__(self):

        self.state = PersonState.UNKNOWN

        self.person_id = 0
        self.user_id = 0
        self.location = [3., 0., 0.]
        self.looking_at_robot = 0.

        self._engagement_start_time = 0
        self._disengagement_start_time = 0

    def __str__(self):
        return "<Person %s>" % self.person_id

    def is_mock_person(self):
        return self.person_id < 0


    def distance(self):
        x,y,z=self.location
        return math.sqrt(x*x+y*y+z*z)

    def distance_to(self, x, y, z):
        x1,y1,z1=self.location
        return math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1)+(z-z1)*(z-z1))

    def is_engaged(self):
        return self.state in [PersonState.ENGAGED, PersonState.DISENGAGING]

    def update(self):
        """
        Returns: True if the person's state has not changed, False otherwise.
        """

        oldstate = self.state

        ###############################################################################
        if self.state == PersonState.UNKNOWN:

            if self.person_id != 0:
                self.state = PersonState.SEEN

        ###############################################################################
        if self.state == PersonState.SEEN:

            if self.user_id > 0 or self.is_mock_person():
                self.state = PersonState.IDENTIFIED

        ###############################################################################
        if self.state == PersonState.IDENTIFIED:

            if self.user_id <= 0 and not self.is_mock_person():
                self.state = PersonState.SEEN

            elif self.distance() < Person.ENGAGEMENT_DISTANCE \
               and (self.looking_at_robot > 0.3 or self.is_mock_person()):

                   self.state = PersonState.ENGAGING
                   self._engagement_start_time = time.time()

        ###############################################################################
        if self.state == PersonState.ENGAGING:

            if not (self.distance() < Person.ENGAGEMENT_DISTANCE \
                    and (self.looking_at_robot > 0.3 or self.is_mock_person())):

                self.state = PersonState.IDENTIFIED

            elif time.time() - self._engagement_start_time > Person.ENGAGEMENT_MIN_DURATION:
                self.state = PersonState.ENGAGED

        ###############################################################################
        if self.state == PersonState.ENGAGED:

            if self.distance() > Person.ENGAGEMENT_DISTANCE:

                self.state = PersonState.DISENGAGING
                self._disengagement_start_time = time.time()

        ###############################################################################
        if self.state == PersonState.DISENGAGING:

            if self.distance() < Person.ENGAGEMENT_DISTANCE \
               and (self.looking_at_robot > 0.3 or self.is_mock_person()):
                self.state = PersonState.ENGAGED

            elif time.time() - self._disengagement_start_time > Person.DISENGAGEMENT_MIN_DURATION:
                self.state = PersonState.IDENTIFIED

        if oldstate != self.state:
            logger.info("%s: new state <%s>" % (self, self.state))
            return False
        else:
            return True
