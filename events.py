
class ActivityEvent:

    # type
    INTERRUPTED = "interrupted"
    NO_ONE_ENGAGED = "interrupted - no one engaged"

    # source
    CTRL_TABLET = "ctrl tablet"
    PEPPER_TABLET = "Pepper tablet"

    def __init__(self, type, src=None):
        self.type = type
        self.src = src

    def __str__(self):
        if self.src:
            return "%s from %s" % (self.type, self.src)
        else:
            return self.type
