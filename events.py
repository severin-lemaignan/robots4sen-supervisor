
class Event:

    # type
    NO_EVENT = "no event"
    INTERRUPTED = "interrupted"
    NO_ONE_ENGAGED = "interrupted - no one engaged"
    NO_INTERACTION = "no interaction"
    ACTIVITY_REQUEST = "activity request"
    ONE_TO_ONE_ENGAGEMENT = "one to one engagement"
    MULTI_ENGAGEMENT = "multi-party engagement"

    # source
    CTRL_TABLET = "ctrl tablet"
    PEPPER_TABLET = "Pepper tablet"

    def __init__(self, type = NO_EVENT, src=None, activity=None, nb_children=0):
        self.type = type
        self.src = src
        self.activity = activity
        self.nb_children = nb_children

    def __str__(self):
        return self.type + \
                    ((" (%s)") % self.activity if self.activity else "") + \
                    ((" from %s" % self.src) if self.src else "")
