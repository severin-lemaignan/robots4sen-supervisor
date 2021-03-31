
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("logger")

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer
import qi

class People(QObject):

    def __init__(self):
        QObject.__init__(self)

        self._people = {}

    onNewPerson = Signal(QObject)

    def update(self):

        p = self.add_person("hello")
        p.setlocation([p.x + 5, p.y, 0])
        return

        # TODO: be more clever: only update coordinates when they are significantly different
        self._people = {}

        for id in self.almemory.getData("PeoplePerception/PeopleList"):
             self._people[str(id)] = self.almemory.getData("PeoplePerception/Person/%s/PositionInTorsoFrame" % id)

        self.person = Person('612102')
        self.person.setlocation([1.4263619184494019, 0.09372032433748245, 0.48271995782852173])
        self._people = [self.person,]

        return self._people

    def add_person(self, id):

        if id in self._people:
            print("Python: person %s is already known. Skipping" % id)
            return self._people[id]

        print("Python: adding new person %s" % id)
        self._people[id] = Person(id)
        self.onNewPerson.emit(self._people[id])

        return self._people[id]



class Person(QObject):

    def __init__(self, id):
        QObject.__init__(self)

        self._id = id
        self._location = [0., 0., 0.]

    def setlocation(self, location):
        self._location = location
        self.x_changed.emit(self.x)
        self.y_changed.emit(self.y)
        self.moved.emit()

    def _get_id(self):
        return self._id

    id = Property(str, _get_id, constant=True)

    moved = Signal()

    x_changed = Signal(float)
    @Property(float, notify=x_changed)
    def x(self):
        return self._location[0]

    y_changed = Signal(float)
    @Property(float, notify=y_changed)
    def y(self):
        return self._location[1]





class NaoqiBridge(QObject):

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


    def connectToRobot(self):

        if self._connected:
            return True

        try:
            logger.info("Trying to connect to %s:%s..." % (self._ip, self._port))
            self._session.connect("tcp://" + self._ip + ":" + self._port)
        except RuntimeError:
            logger.error("Can't connect to Naoqi at ip \"" + self._ip + "\" on port " + self._port +".\n"
               "Please check your script arguments. Run with -h option for help.")
        
            self._connected = False
            return False

        self.almotion = self._session.service("ALMotion")
        self.albattery = self._session.service("ALBattery")
        self.almemory = self._session.service("ALMemory")
        self.alanimationplayer = self._session.service("ALAnimationPlayer")
        self.alpeople = self._session.service("ALPeoplePerception")
        
        logger.info("Robot connected!")
        self._connected = True
        self.isConnected_changed.emit(self._connected)


        self.configureRobot()

        return True

    def configureRobot(self):
        self.almotion.setOrthogonalSecurityDistance(0.1)
        self.almotion.setTangentialSecurityDistance(0.05)

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
            plugged = self.almemory.getData("Device/SubDeviceList/Battery/Charge/Sensor/Power") > 0
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
    def animate(self, animation):
        """
        Argument is one of the available animation tag. See
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html#animationplayer-tags-pepper
        """

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'animate'")
            return

        logging.debug("Running animation tag <%s>" % animation)
        future = self.alanimationplayer.runTag("hello", _async=True)
        future.value() # wait until the animation is complete


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


