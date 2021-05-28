
import logging;logger = logging.getLogger("robots.naoqibridge")

import json
from Queue import Queue
import re
import time
import math

import qi

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer


from constants import *
from csv_logging import create_csv_logger

from websocketserver import TabletWebSocketServer

from person import Person, PersonState

people_logger = create_csv_logger("logs/people.csv")

almemory = None
alusersession = None

class MockFuture():
    def __init__(self, waiting_time = 1):
        self.waiting_time = waiting_time

    def wait(self):
        time.sleep(self.waiting_time)

    def isRunning(self):
        return False

    def isFinished(self):
        return True

class People(QObject):

    PEOPLE_UPDATE_INTERVAL = 200 #ms
    PEOPLE_LOGGING_INTERVAL = 1000 #ms

    def __init__(self):
        QObject.__init__(self)

        self._people = {}

        self.mock_id_idx = -1
        self._mock_people = set()

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(People.PEOPLE_UPDATE_INTERVAL)
        self._watchdog_timer.timeout.connect(self.update)
        self._watchdog_timer.start()

    newPerson = Signal(str, bool, str) # str: person id; bool: true -> auto tracked; false: manually tracked; str -> age group (child or adult)
    disappearedPerson = Signal(str)

    @Slot(str)
    def createMockPerson(self, type):
        logger.warning("Adding a mock %s" % type)

        self._people[self.mock_id_idx] = Person(self.mock_id_idx)
        self.newPerson.emit(str(self.mock_id_idx), False, type)
        self._mock_people.add(self.mock_id_idx)

        self.mock_id_idx -= 1

    def update(self):

        # connected yet?
        if not almemory:
            return

        detected_ids = set(almemory.getData("PeoplePerception/PeopleList"))
        detected_ids = detected_ids | self._mock_people

        #print("UserSession:" + str(alusersession.getOpenUserSessions()))
        #for user_id in alusersession.getOpenUserSessions():
        #    ppid = alusersession.getPpidFromUsid(user_id)
        #    print("User <%s> -> Person <%s>" % (user_id, ppid))

        current_ids = set(self._people.keys())
        new_ids = detected_ids - current_ids
        vanished_ids = current_ids - detected_ids

        for id in new_ids:
            logger.debug("New person <%s>" % id)

            if id > 0: # else, signal already emitted in createMockPerson()
                self._people[id] = Person(id)
                self.newPerson.emit(str(id), True, NaoqiPerson.AGE_UNKNOWNN)


        for id in vanished_ids:
            logger.debug("Person <%s> disappeared" % id)
            self.disappearedPerson.emit(str(id))
            del(self._people[id])

    def getperson(self, id):
        return self._people[id]

    def getpeople(self):
        return self._people

    def getengagedpeople(self):
        return set([p for id, p in self._people.items() if p.is_engaged()])

    def delete(self, id):
        logger.debug("Person <%s> deleted" % id)
        self.disappearedPerson.emit(str(id))
        del(self._people[id])


# !! creating a global here !!
# needed for each Person instance (created from QML) to add itself to the list of
# people
# instantiated in main.py
people = None

class NaoqiPerson(QObject):

    def __init__(self):
        QObject.__init__(self)

        # the Person class manages the engagement state machine
        self.person = None


        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(People.PEOPLE_UPDATE_INTERVAL)
        self._watchdog_timer.timeout.connect(self.update)
        self._watchdog_timer.start()

        self._logging_timer = QTimer(self)
        self._logging_timer.setInterval(People.PEOPLE_LOGGING_INTERVAL)
        self._logging_timer.timeout.connect(self.log)
        self._logging_timer.start()

    def update(self):

        if not self.person:
            return

        # we are connected to naoqi
        if almemory and not self.person.is_mock_person():

            self.person.user_id = alusersession.getUsidFromPpid(self.person.person_id)


            #####################
            ##   LOCATION
            try:
                self.person.world_location = almemory.getData("PeoplePerception/Person/%s/PositionInWorldFrame" % self.person.person_id)
                local_pose = almemory.getData("PeoplePerception/Person/%s/PositionInRobotFrame" % self.person.person_id)
                self.setlocation(local_pose)

            except RuntimeError as re:
                # almemory keys missing for that person -> person not seen anymore!
                logger.info("%s not seen anymore" % self.person)
                self.setlocation([0,0,0])

            #######################
            ##   GAZE DIRECTION
            try:
                looking_at_robot = almemory.getData("PeoplePerception/Person/%s/LookingAtRobotScore" % self.person.person_id)

                if abs(looking_at_robot - self.person.looking_at_robot) > 0.05:
                    self.person.looking_at_robot = looking_at_robot
                    self.looking_at_robot_changed.emit(looking_at_robot)
            except RuntimeError:
                if self.person.looking_at_robot != 0:
                    self.person.looking_at_robot = 0
                    self.looking_at_robot_changed.emit(0)


            ######################
            ##   AGE
            try:
                age_estimate = almemory.getData("PeoplePerception/Person/%s/AgeProperties" % self.person.person_id)
                if age_estimate:
                    age, confidence = age_estimate
                    if confidence > 0.3:
                        self.setage(self.ADULT if age > 17 else self.CHILD)
            except RuntimeError:
                pass



        is_state_same = self.person.update()
        if not is_state_same:
            self.state_changed.emit(self.person.state.value)
            if self.person.state.value == PersonState.LOST:
                self.delete()


    def log(self):

        if self.person.state.value != PersonState.UNKNOWN:
            people_logger.info((
                                    self.person.person_id,
                                    self.person.user_id,
                                    self.person.location[0],
                                    self.person.location[1],
                                    self.person.location[2],
                                    self.person.world_location[0],
                                    self.person.world_location[1],
                                    self.person.world_location[2],
                                    self.person.looking_at_robot,
                                    self.person.state,
                                    self.person.age
                                )
                              )

    moved = Signal()

    @Slot()
    def delete(self):
        people.delete(self.person.person_id)

    @Slot(list) # the slot is used when we 'mock' users, to set their positions
    def setlocation(self, location):
        if self.person.distance_to(*location) < 0.1: # less than 10cm? don't update
            return

        self.person.location = location
        self.x_changed.emit(self.x)
        self.y_changed.emit(self.y)
        self.moved.emit()

    person_id_changed = Signal(str)

    def set_person_id(self, id):
        self.person = people.getperson(int(id))
        self.person_id_changed.emit(str(id))
        logger.info("Person id now %s" % self.person.person_id)

    def get_person_id(self):
        return str(self.person.person_id)

    person_id = Property(str, get_person_id, set_person_id, notify=person_id_changed)

    x_changed = Signal(float)
    @Property(float, notify=x_changed)
    def x(self):
        return self.person.location[0]

    y_changed = Signal(float)
    @Property(float, notify=y_changed)
    def y(self):
        return self.person.location[1]

    looking_at_robot_changed = Signal(float)
    @Property(float, notify=looking_at_robot_changed)
    def looking_at_robot(self):
        return self.person.looking_at_robot

    state_changed = Signal(str)
    @Property(str, notify=state_changed)
    def state(self):
        return self.person.state.value

    def setage(self, age):

        if age == Person.ADULT:

            if self.person.age == Person.AGE_UNKNOWNN or self.person.age == Person.CHILD:
                logger.warning("%s detected as an adult" % self.person)
                self.person.age = Person.ADULT
                self.age_changed.emit(self.person.age)
        else:
            if self.person.age == Person.AGE_UNKNOWNN or self.person.age == Person.ADULT:
                logger.warning("%s detected as a child" % self.person)
                self.person.age = Person.CHILD
                self.age_changed.emit(self.person.age)



    age_changed = Signal(str)
    def getage(self):
        return self.person.age

    age = Property(str, getage, setage, notify=age_changed)


class NaoqiBridge(QObject):

    SPEAKING_RATE = 75 # %
    WATCHDOG_INTERVAL = 200 #ms

    STOP = "STOP"
    FORWARDS = "FORWARDS"
    BACKWARDS = "BACKWARDS"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"

    isConnected_changed = Signal(bool)
    isPlugged_changed = Signal(bool)
    battery_changed = Signal(float)

    def __init__(self, args):
        global people

        QObject.__init__(self)

        self._with_robot = not args.no_robot

        self._ip = args.ip
        self._port = str(args.port)

        if self._with_robot:
            import qi
            self._session = qi.Session()

        self._connected = False
        self._plugged = False
        self._battery_level = 0.5

        people = People()
        self._people = people # !! using the `people` global

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(NaoqiBridge.WATCHDOG_INTERVAL)
        self._watchdog_timer.timeout.connect(self.checkAlive)
        self._watchdog_timer.start()

        self.isConnected_changed.connect(self.on_isConnected_changed)

        if self._with_robot:
            self.connectToRobot()
        else:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
            except:
                logger.error("No speech engine installed. Install pyttsx3 to mock out speech synthesis.")
                self.tts_engine = None



        # creates the websocket server to control the tablet content.
        # note that this server *must* run from the main thread (eg, the Qt app thread)
        self.tablet = TabletWebSocketServer()

        # cmd_queue is set in main.py to point to the supervisor cmd_queue
        self.cmd_queue = None

    def tearDown(self):
        if self._with_robot:
            self.altablet.hideWebview()

    def connectToRobot(self):
        global almemory, alusersession

        if self._connected:
            return True

        try:
            logger.info("Trying to connect to %s:%s..." % (self._ip, self._port))
            self._session.connect("tcp://" + self._ip + ":" + self._port)
        except RuntimeError:
            raise RuntimeError("Can't connect to Naoqi at ip \"" + self._ip + "\" on port " + self._port +".\n"
               "Please check your script arguments. Run with -h option for help.")

        

        self.almotion = self._session.service("ALMotion")
        self.altracker = self._session.service("ALTracker")
        self.albattery = self._session.service("ALBattery")
        self.alanimatedspeech = self._session.service("ALAnimatedSpeech")

        self.albehaviours = self._session.service("ALBehaviorManager")

        try:
            self.altablet = self._session.service("ALTabletService")
            self.alphoto = self._session.service("ALPhotoCapture")
        except RuntimeError:
            logger.warning("Some AL services are not available! Running in simulator?")
            self.altablet = None
            self.alphoto = None

        almemory = self._session.service("ALMemory")
        self.alanimationplayer = self._session.service("ALAnimationPlayer")
        self.alpeople = self._session.service("ALPeoplePerception")
        alusersession = self._session.service("ALUserSession")
        

        logger.info("Robot connected!")
        self._connected = True
        self.isConnected_changed.emit(self._connected)


        self.configureRobot()

        return True

    def configureRobot(self):
        self.almotion.setOrthogonalSecurityDistance(0.1)
        self.almotion.setTangentialSecurityDistance(0.05)

        logger.info("Available robots4SEN behaviours: %s" % ", ".join(self.getBehaviours()))


    def connectTablet(self, ssid, encryption="open", passwd="", force=False):

        if not self._with_robot or not self.altablet:
            logger.warning("No Pepper tablet!")
            return

        if not passwd:
            encryption = "open"

        logger.info("Configuring and connecting the robot's tablet to wifi network <%s>. Please wait..." % ssid)

        if not force and self.altablet.getWifiStatus() == "CONNECTED":
            self.altablet.resetTablet() # clears the webbrowser cache
            logger.info("Pepper's tablet already connected. Skipping.")
            return

        logger.debug("Disconnecting wifi first...")
        ok = False
        while not self.altablet.getWifiStatus() == "DISCONNECTED":
            ok = self.altablet.disconnectWifi()

        self.altablet.enableWifi()
        ok = self.altablet.configureWifi(encryption, ssid, passwd)
        if not ok:
            raise RuntimeError("Impossible to connect Pepper's tablet to the wifi network: configuration invalid (ssid: %s, pass: %s, encryption: %s)" % (ssid, passwd, encryption))

        ok = self.altablet.connectWifi(ssid)
        if not ok:
            raise RuntimeError("Impossible to connect Pepper's tablet to the wifi network. Error while attempting to connect")

        MAX_WAIT_TIME_WIFI_CONNECTION = 10 #sec
        total_time = 0
        while self.altablet.getWifiStatus() != "CONNECTED":
            time.sleep(0.4)
            total_time += 0.4
            logger.debug("Pepper's tablet wifi status: %s" % self.altablet.getWifiStatus())

            if total_time > MAX_WAIT_TIME_WIFI_CONNECTION:
                raise RuntimeError("Impossible to connect Pepper's tablet to the wifi network <%s>. After %ssec, status is <%s>" % (ssid, MAX_WAIT_TIME_WIFI_CONNECTION, self.altablet.getWifiStatus()))

        self.altablet.resetTablet() # clears the webbrowser cache
        logger.info("Pepper's tablet successfully connected.")



    @Slot(str)
    def setTabletUrl(self, url):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: setTAbletUrl: %s" % url)
            return

        if not self.altablet:
            logger.warning("No Pepper tablet!")
            return


        logger.info("Setting the robot's tablet to <%s>" % url)
        self.altablet.showWebview(url)


    def checkAlive(self):

        if not self._with_robot:
            return


        if not self._connected:
            # try to reconnect...
            if not self.connectToRobot():
                return

        try:
            self._battery_level = self.albattery.getBatteryCharge()/100.
        except RuntimeError:
            if self._connected:
                logger.error("Robot disconnected!")
                self._connected = False
                self.isConnected_changed.emit(self._connected)
            return

        self.battery_changed.emit(self._battery_level)

        try:
            plugged = almemory.getData("Device/SubDeviceList/Battery/Charge/Sensor/Power") > 0
        except RuntimeError:
            # not connected to the real robot -- the ALMemory key does not exist
            plugged = False

        if plugged != self._plugged:
            logger.warning("Robot plugged status = %s" % plugged)
            self._plugged = plugged
            self.isPlugged_changed.emit(self._plugged)



    @Property(bool, notify=isConnected_changed)
    def connected(self):
        return self._connected

    @Property(bool, notify=isPlugged_changed)
    def plugged(self):
        return self._plugged

    @Property(float, notify=battery_changed)
    def battery(self):
        return self._battery_level

    def _get_people(self):
        return self._people
    people = Property(QObject, _get_people, constant=True)

    @Slot()
    def on_isConnected_changed(self, value):
        logging.warning("Connection status changed! connected=%s" % value)


    @Slot(str)
    def request_animate(self, animation):
        """
        Argument is one of the available animation tag. See
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html#animationplayer-tags-pepper
        """
        
        self.cmd_queue.put((CTRL, SOCIAL_GESTURE, animation))


    def animate(self, animation):
        """
        Argument is one of the available animation tag. See
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html#animationplayer-tags-pepper
        """
        if not self._with_robot:
            logger.warning("MOCK ROBOT: animate: %s" % animation)
            return

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'animate'")
            return

        logging.debug("Running animation tag <%s>" % animation)
        future = self.alanimationplayer.runTag(animation, _async=True)
        future.value() # wait until the animation is complete

    @Slot(str)
    def request_behaviour(self, behaviour):
        """
        Argument is one of the available installed behaviour.
        """
        
        self.cmd_queue.put((CTRL, BEHAVIOUR, behaviour))


    def run_behaviour(self, behaviour):
        """
        Argument is one of the available installed behaviour.
        """

        if not self._with_robot:
            logger.warning("MOCK ROBOT: run_behaviour: %s" % behaviour)
            return MockFuture()

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'run_behaviour'")
            return

        logging.debug("Running behaviour <%s>" % behaviour)
        return qi.async(self.albehaviours.runBehavior, behaviour)

    @Slot(str)
    def request_activity(self, activity):
        """
        Argument is one of the available installed behaviour.
        """
        
        self.cmd_queue.put((CTRL, ACTIVITY, activity))


    @Slot()
    def getBehaviours(self):
        if not self._with_robot:
            logger.warning("MOCK ROBOT: getBehaviour")
            return ["robots4sen-brl/mock_behaviour1","robots4sen-brl/mock_behaviour2"]

        behaviours = [b for b in self.albehaviours.getInstalledBehaviors() if b.startswith("robots4sen")]


        return behaviours

    @Slot(str)
    def request_track(self, person_id):
        self.cmd_queue.put((CTRL, TRACK, person_id))

    def track(self, person_id):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: track: %s" % person_id)
            return

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'track'")
            return

        self.altracker.registerTarget("People", [person_id,])
        self.altracker.track("People")


    @Slot()
    def request_stop_tracking(self):
        self.cmd_queue.put((CTRL, TRACK, ""))

    def stop_tracking(self):
        if not self._with_robot:
            logger.warning("MOCK ROBOT: stop_tracking")
            return

        self.altracker.stopTracker()
        self.altracker.unregisterAllTargets()


    @Slot(float, float, float)
    def request_lookAt(self, x, y, z):
        self.cmd_queue.put((CTRL, LOOK_AT, (x, y, z)))

    def lookAt(self, x, y, z):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: lookAt: %s %s %s" % (x,y,z))
            return

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'lookAt'")
            return

        self.altracker.lookAt([x, y, z], 0.7, True) # pos, fraction speed, whole body

    def glanceAtTablet(self):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: glanceAtTablet")
            return

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'glanceAtTablet'")
            return

        logger.info("Looking at tablet")
        #self.altracker.lookAt([0.2, 0, 0], 1, True)
        return qi.async(self.altracker.lookAt, [0.2, 0, 0], 0.5, False) # pos, fraction speed, whole body


    def extract_options(self, raw):
        option_re = r'\\option=(.*?)\\'
        text = re.sub(option_re,"", raw)
        options = re.findall(option_re,raw)
        options = [json.loads(o) for o in options]
        return text.strip(), options

    @Slot(str)
    def say(self, text):
        """Returns a future on the 'say' action
        """

        text, options = self.extract_options(text)
        if options:
            self.tablet.setOptions(options)

        if text:

            if not self._with_robot:
                logger.warning("MOCK ROBOT: say: %s" % text)
                if self.tts_engine:
                    option_re = r'\\.*?\\|\^.*?\)' # remove annotations like \pau=...\ and ^start(...)
                    text = re.sub(option_re,"", text)
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                return MockFuture()


            if not self._connected:
                logger.warning("Robot not connected. Can not perform 'say'")
                return

            return qi.async(self.alanimatedspeech.say, "\\rspd=%s\\" % self.SPEAKING_RATE + text)

        else:
            return MockFuture(0)

    @Slot()
    def rest(self):
        
        if not self._with_robot:
            logger.warning("MOCK ROBOT: rest")
            return

        self.almotion.rest()

    @Slot()
    def wakeup(self):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: wakeup")
            return

        self.almotion.wakeUp()

    @Slot()
    def toggleArmsStiffness(self):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: toggleArmsStiffness")
            return

        s = self.almotion.getStiffnesses("RArm")[0]
        logger.debug("Current arm stiffness: %s" % s)
        self.almotion.stiffnessInterpolation(["RArm", "LArm"], 0.0 if s > 0.2 else 1.0, 1.0)


    @Slot(str, bool)
    def move(self, direction, active):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: move: %s (active: %s)" % (direction, active))
            return

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'move'")
            return

        if direction == NaoqiBridge.STOP:
            self.almotion.stopMove()

        elif direction == NaoqiBridge.FORWARDS:
            if active:
                self.almotion.moveToward(0.6,0,0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.BACKWARDS:
            if active:
                self.almotion.moveToward(-0.4,0,0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.LEFT:
            if active:
                self.almotion.moveToward(0,0.3, 0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.RIGHT:
            if active:
                self.almotion.moveToward(0,-0.3, 0)
            else:
                self.almotion.stopMove()
        elif direction == NaoqiBridge.TURN_RIGHT:
            if active:
                self.almotion.moveToward(0,0, -0.3)
            else:
                self.almotion.stopMove()
        elif direction == NaoqiBridge.TURN_LEFT:
            if active:
                self.almotion.moveToward(0,0, 0.3)
            else:
                self.almotion.stopMove()


    @Slot()
    def prepare_take_picture(self):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: prepare_take_picture")
            return

        if not self.alphoto:
            logger.warning("ALPhotoCapture not initialised. Skipping")
            return

        logger.info("Preparing to take picture...")
        self.alphoto.setResolution(4) # 2560*1920px -- cf http://doc.aldebaran.com/2-5/family/pepper_technical/video_2D_pep_v18a.html#cameraresolution-ov5640
        self.alphoto.setPictureFormat("jpg")
        self.alphoto.setHalfPressEnabled(True) # pre-subscribe to ALVideoDevice, for higher photo reactivity

    @Slot()
    def take_picture(self):

        if not self._with_robot:
            logger.warning("MOCK ROBOT: take_picture")
            return

        if not self.alphoto:
            logger.warning("ALPhotoCapture not initialised. Skipping")
            return

        logger.info("Taking picture!")
        self.alphoto.takePicture("/home/nao/recordings/", "robots4sen")
        self.alphoto.setHalfPressEnabled(False) # usubscribe from ALVideoDevice
