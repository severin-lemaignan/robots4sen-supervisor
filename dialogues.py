import random

DIALOGUES = {
    "story_prompt": ["I love stories! Let's find one!",
                    "You want to listen to a story? Great!",
                    "Let see what story we can come up with...",
                    "Ok! Let me tell you a story."],
    "story_start": ["Alright, let start the story.", 
                    "Good, good! Let's start the story"],
    "story_end": ["The story is finished! I hope you liked it.",
                  "The end. Did you like the story?"]
    }

def get_dialogue(type):
    return random.choice(DIALOGUES[type])
