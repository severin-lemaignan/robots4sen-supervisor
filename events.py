
class ActivityEvent:
    INTERRUPTED = "interrupted"
    NO_ONE_ENGAGED = "no one engaged"

    def __init__(self, type):
        self.type = type
