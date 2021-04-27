
import logging;logger = logging.getLogger("robots.naoqibridge")

from Queue import Queue

import time

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer

import qi

from constants import *

almemory = None
alusersession = None

class People(QObject):

    def __init__(self):
        QObject.__init__(self)

        self._people = set()

    newPerson = Signal(str)
    disappearedPerson = Signal(str)

    def update(self):

        # connected yet?
        if not almemory:
            return

        ids = set([str(id) for id in almemory.getData("PeoplePerception/PeopleList")])

        #print("UserSession:" + str(alusersession.getOpenUserSessions()))
        #for user_id in alusersession.getOpenUserSessions():
        #    ppid = alusersession.getPpidFromUsid(user_id)
        #    print("User <%s> -> Person <%s>" % (user_id, ppid))

        new_ids = ids - self._people
        vanished_ids = self._people - ids

        for id in new_ids:
            logger.debug("New person <%s>" % id)
            self.newPerson.emit(id)

        for id in vanished_ids:
            logger.debug("Person <%s> disappeared" % id)
            self.disappearedPerson.emit(id)

        self._people = ids


class Person(QObject):

    def __init__(self):
        QObject.__init__(self)

        self._person_id = 0
        self._user_id = 0
        self._location = [0., 0., 0.]

        self.visible = True

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(NaoqiBridge.PEOPLE_UPDATE_INTERVAL)
        self._watchdog_timer.timeout.connect(self.update)
        self._watchdog_timer.start()


    def update(self):

        # connected yet?
        if not almemory:
            return

        old_user_id = self._user_id
        self._user_id = alusersession.getUsidFromPpid(self._person_id)
        if self._user_id != old_user_id:
            self.known_changed.emit(self.known)

        try:
            pose = almemory.getData("PeoplePerception/Person/%s/PositionInRobotFrame" % self._person_id)
            self.setlocation(pose)

        except RuntimeError:
            self.visible = False


    def setlocation(self, location):
        #TODO OPTIMIZATION: if new location close to prev, do not update
        if location == self._location:
            return

        self._location = location
        self.x_changed.emit(self.x)
        self.y_changed.emit(self.y)
        self.moved.emit()

    person_id_changed = Signal(str)

    def set_person_id(self, id):
        self._person_id = int(id)
        self.person_id_changed.emit(str(id))
        logger.info("Person id now %s" % self._person_id)

    def get_person_id(self):
        return str(self._person_id)

    person_id = Property(str, get_person_id, set_person_id, notify=person_id_changed)


    moved = Signal()

    known_changed = Signal(bool)
    @Property(bool, notify=known_changed)
    def known(self):
        return self._user_id != 0

    x_changed = Signal(float)
    @Property(float, notify=x_changed)
    def x(self):
        return self._location[0]

    y_changed = Signal(float)
    @Property(float, notify=y_changed)
    def y(self):
        return self._location[1]





class NaoqiBridge(QObject):

    SPEAKING_RATE = 75 # %
    WATCHDOG_INTERVAL = 200 #ms
    PEOPLE_UPDATE_INTERVAL = 200 #ms

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
        QObject.__init__(self)

        self._ip = args.ip
        self._port = str(args.port)
        self._session = qi.Session()

        self._connected = False
        self._plugged = False
        self._battery_level = 0.5

        self._people = People()

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(NaoqiBridge.WATCHDOG_INTERVAL)
        self._watchdog_timer.timeout.connect(self.checkAlive)
        self._watchdog_timer.start()

        self.isConnected_changed.connect(self.on_isConnected_changed)

        self.connectToRobot()

        # cmd_queue is set in main.py to point to the supervisor cmd_queue
        self.cmd_queue = None

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

    def connectTablet(self, ssid, encryption="open", passwd=""):

        if not self.altablet:
            logger.warning("No Pepper tablet!")
            return

        if not passwd:
            encryption = "open"

        logger.info("Configuring and connecting the robot's tablet to wifi network <%s>. Please wait..." % ssid)

        #self.altablet.disableWifi()
        self.altablet.enableWifi()
        ok = self.altablet.configureWifi(encryption, ssid, passwd)
        if not ok:
            raise RuntimeError("Impossible to connect Pepper's tablet to the wifi network: configuration invalid (%s:%s, %s)" % (ssid, passwd, encryption))

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

        logger.info("Pepper's tablet successfully connected.")



    @Slot(str)
    def setTabletUrl(self, url):

        if not self.altablet:
            logger.warning("No Pepper tablet!")
            return


        logger.info("Setting the robot's tablet to <%s>" % url)
        self.altablet.showWebview(url)


    def checkAlive(self):

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

        self.people.update()


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

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'animate'")
            return

        logging.debug("Running animation tag <%s>" % animation)
        future = self.alanimationplayer.runTag(animation, _async=True)
        future.value() # wait until the animation is complete

    @Slot(str)
    def request_track(self, person_id):
        self.cmd_queue.put((CTRL, TRACK, person_id))

    def track(self, person_id):

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'track'")
            return

        self.tracker.registerTarget("People", [person_id,])
        self.tracker.track("People")


    @Slot()
    def request_stop_tracking(self):
        self.cmd_queue.put((CTRL, TRACK, ""))

    def stop_tracking(self):
        self.tracker.stopTracker()
        self.tracker.unregisterAllTargets()


    @Slot(float, float, float)
    def request_lookAt(self, x, y, z):
        self.cmd_queue.put((CTRL, LOOK_AT, (x, y, z)))

    def lookAt(self, x, y, z):

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'lookAt'")
            return

        self.tracker.lookAt([x, y, z], 0.7, True) # pos, fraction speed, whole body

    @Slot(str)
    def say(self, text):
        """Returns a future on the 'say' action
        """

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'say'")
            return

        return qi.async(self.alanimatedspeech.say, "\\rspd=%s\\" % self.SPEAKING_RATE + text)

    @Slot(str, bool)
    def move(self, direction, active):

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
        if not self.alphoto:
            logger.warning("ALPhotoCapture not initialised. Skipping")
            return

        logger.info("Preparing to take picture...")
        self.alphoto.setResolution(4) # 2560*1920px -- cf http://doc.aldebaran.com/2-5/family/pepper_technical/video_2D_pep_v18a.html#cameraresolution-ov5640
        self.alphoto.setPictureFormat("jpg")
        self.alphoto.setHalfPressEnabled(True) # pre-subscribe to ALVideoDevice, for higher photo reactivity

    @Slot()
    def take_picture(self):
        if not self.alphoto:
            logger.warning("ALPhotoCapture not initialised. Skipping")
            return

        logger.info("Taking picture!")
        self.alphoto.takePicture("/home/nao/recordings/", "robots4sen")
        self.alphoto.setHalfPressEnabled(False) # usubscribe from ALVideoDevice
