import random

DIALOGUES = {
    "story_prompt": ["I love stories! Let's find one!",
                    "You want to listen to a story? Great!",
                    "Let see what story we can come up with...",
                    "Ok! Let me tell you a story."]
    }

def get_dialogue(type):
    return random.choice(DIALOGUES[type])