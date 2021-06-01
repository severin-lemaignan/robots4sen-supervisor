import logging
logger = logging.getLogger("robots.activities.fun_dances")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

class FunDancesActivity(Activity):

    type = FUN_DANCES

    def __init__(self):
        super(FunDancesActivity, self).__init__()

        self.stop_behaviour = False

    def run(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("fun_dances_start")).wait()
        yield RUNNING

        behaviours = ["robots4sen-brl/saxophone",
                  "robots4sen-brl/macarena",
                  "robots4sen-brl/disco"]

        behaviour = self.robot.run_behaviour(random.choice(behaviours))

        while behaviour.isRunning():
            if self.stop_behaviour:
                behaviour.cancel()
                self.stop_behaviour = False
            yield RUNNING

    def on_no_one_engaged(self, evt):
        logger.warning("No one detected anymore. Ignoring it as I'm dancing and not paying attention to my surroundings.");

        return RUNNING

    def terminate(self):
        self.stop_behaviour = True
        next(self._behaviour) # run it one more time to ensure the naoqi behaviour is cancelled
        return INTERRUPTED

activity = FunDancesActivity()

def get_activity():
    return activity
