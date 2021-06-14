import random
from constants import *

DIALOGUES = {
    "story_prompt":         ["I love stories! ^startTag(estimate)Let's find one!",
                            "^startTag(enthusiatic)You want to listen to a story? Great!",
                            "^startTag(think)Let see what story we can come up with...",
                            "Ok! Let me tell you a story."],

    "story_start":          ["Alright, let start the story.",
                            "Good, good! Let's start the story",
                            "Time for a story"],

    "story_end":            ["The story is finished! I hope you liked it.",
                            "The end. Did you like the story?",
                            "That's the end of the story, what do you think?"],
    "story_interrupted":    ["\\pau=500\\Alright, I stop the story."],
    "story_no_one_left":    ["\\pau=500\\^startTag(disappointed)No one to listen to my story? Alright."],

    "listening_prompt":     ["Tell me! I'm listening",
                            "What do you want to tell me? I'm listening!",
                            "Sure, happy to listen to you"],

    "listening_end":        ["Thank you!",
                            "Thank you for telling me."],

    "listening_no_one_left":    ["^startTag(disappointed)You are gone? alright."],

    "jokes_start":          ["^startTag(excited)Joke time!\\pau=500\\",
                            "^startTag(estimate)Let me think of a good joke...\\pau=700\\"],

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

    "multiparty_prompt":    ["^startTag(excited)Hi! Good to see you!",
                             "^startTag(excited)Hi! How are you?"
                             ],

    "multiparty_end":    ["Bye! See you soon!",
                          "Bye bye",
                          "See you!",
                          "See you soon!",
                          "Have fun! Bye!"
                        ],

    "mood_prompt_activities": ["What do you want to do?",
                              "So. What do you feel like doing?",
                              "Let see what we can do.",
                              "What should we do?",
                              "What do you like to do?",
                              "What would you like to do?"],

    "mood_all_activities":    ["Alright, here other options.",
                               "Ok, here some more activities.",
                               "Alright, you want to do something else. Let see."],

    "mood_prompt_continuation": ["Do you want to do something else?",
                              "You want to continue?",
                              "You want another activity?",
                              "We do something else?",
                              "Do you want to continue?"],

    "mood_end":             ["Ok! How do you feel now?",
                            "Thank you for your time! How do you feel now?",
                            "Feel any different?"],

    "fun_dances_start":     ["Let's dance!",
                            "Time to move our bodies!"],

    "calm_dances_start":     ["^startTag(becalm)Alright, something calm.",
                            "^startTag(becalm)Let's do something slow."],

    "cuddle_start":     ["^startTag(becalm)Okay, let's cuddle.",
                            "^startTag(becalm)Sure! Cuddles are great."],

    "calm_music_start":     ["^startTag(becalm)Let me choose some quiet music to listen.",
                            "^startTag(becalm)Good idea, a bit a calm music."],


    "relax_sounds_start":  ["^startTag(becalm)What about listening to that sound?",
                            "^startTag(becalm)I find that sound relaxing.",
                            "^startTag(becalm)I like that sound."],


    }

ACTIVITIES_DIALOGUES = {
        CALM_DANCES: ['do', 'a dance?', '\\option={"id":"%s","img":"images/calm_dance.svg","label":"Calm dance"}\\' % CALM_DANCES],
        CALM_MUSIC: ['listen', 'some music?', '\\option={"id":"%s","img":"images/music.svg","label":"Music"}\\' % CALM_MUSIC],
        CUDDLE: ['do', 'a cuddle?', '\\option={"id":"%s","img":"images/cuddle.svg","label":"Cuddle"}\\' % CUDDLE],
        FUN_DANCES: ['do', 'a fun dance?', '\\option={"id":"%s","img":"images/party.svg","label":"Fun dance"}\\' % FUN_DANCES],
        JOKES: ['listen', 'a good joke or two?', '\\option={"id":"%s","img":"images/joke.svg","label":"Jokes"}\\' % JOKES],
        LISTENING: ['other', 'simply listen to you?', '\\option={"id":"%s","img":"images/speak.svg","label":"Chat"}\\' % LISTENING],
        RELAX_SOUNDS: ['listen', 'relaxing sounds?', '\\option={"id":"%s","img":"images/relax.svg","label":"Sounds"}\\' % RELAX_SOUNDS],
        ROCK_SCISSOR_PAPER: ['play', 'rock paper scissors?', '\\option={"id":"%s","img":"images/scissors.svg","label":"Game"}\\' % ROCK_SCISSOR_PAPER],
        STORY: ['listen', 'a story?', '\\option={"id":"%s","img":"images/story.svg","label":"Story"}\\' % STORY],
        }

MOODS_FEEDBACK = {
        SAD: ["Oh, sorry to hear that you feel not so good", "You feel a bit down?", "That's ok, let see.", "Ok, thank you for letting me know."],
        HAPPY: ["Cool!", "Good, I like that!", "Good to hear!", "Glad you feel good!", "Cool!", "Nice!"],
        CONFUSED: ["Not too good?","A bit all over the place?", "Let's do something then.", "Ok, let's do something together", "Feeling a bit funny?"],
        ANGRY: ["Oh! You feel angry? Let see.", "You feel angry? Ok, thanks for telling me", "Ok, let see if we can calm down a little then", "That's ok to feel angry."],
        }

FINAL_MOODS_FEEDBACK = {
        SAD: ["Sorry to hear that you still feel sad", "Ok, I hope you will feel better soon."],
        HAPPY: ["Good to hear!", "Glad you feel good!", "Cool!", "Nice!"],
        CONFUSED: ["Not too sure?","Still feeling a bit funny. Well, I hope you enjoyed it anyway.", "Ok. I hope you'll feel calmer soon."],
        ANGRY: ["Oh! You still feel angry? Maybe you should talk to an adult."],
        }

def get_dialogue(type):
    return random.choice(DIALOGUES[type])
