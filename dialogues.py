import random

DIALOGUES = {
    "story_prompt":         ["I love stories! ^startTag(estimate)Let's find one!",
                            "^startTag(enthusiatic)You want to listen to a story? Great!",
                            "^startTag(think)Let see what story we can come up with...",
                            "Ok! Let me tell you a story."],

    "story_start":          ["Alright, let start the story.", 
                            "Good, good! Let's start the story"],

    "story_end":            ["The story is finished! I hope you liked it.",
                            "The end. Did you like the story?"],

    "story_interrupted":    ["\\pau=500\\Alright, I stop the story."],

    "story_no_one_left":    ["\\pau=500\\^startTag(disappointed)No one to listen to my story? Alright."],

    "jokes_start":          ["^startTag(excited)Joke time!",
                            "^startTag(estimate)Let me think of a good joke...\\pau=500\\"],

    "jokes_inbetween":      ["^runTag(happy)Another one!\\pau=500\\",
                             "^runTag(happy)I've got another one!\\pau=500\\",
                             "^runTag(happy)What about that one?\\pau=500\\",
                             "^runTag(happy)Wait, I know another one\\pau=500\\",
                             "^runTag(happy)Ok, that one now!\\pau=500\\",
                             "^runTag(happy)And do you know that one?\\pau=500\\",
                             "^runTag(happy)Do you know that one?\\pau=500\\",
                            ],

    "jokes_end":            ["\\pau=1000\\I love these jokes!",
                            "\\pau=900\\Hope you liked these jokes!"],


    "jokes_no_one_left":    ["\\pau=500\\^startTag(disappointed)You don't like my joke? I need to find better ones then..."],

    "mood_prompt":          ["^startTag(excited)Hey! Good to see you! How do you feel?",
                            "^startTag(happy)Hi! How are you?",
                            "^startTag(happy)Nice to see you! How are you?"],


    "mood_prompt_activities": ["What can we do?",
                              "What should we do?",
                              "What would you like to do?"],

    "fun_dances_start":     ["Let's dance!", 
                            "Time to move our bodies!"],

    }

def get_dialogue(type):
    return random.choice(DIALOGUES[type])
