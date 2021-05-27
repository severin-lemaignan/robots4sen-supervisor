import random
from constants import *

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
                              "So. What do you feel doing?",
                              "Let see what we have.",
                              "What should we do?",
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
        LISTENING: ['other', 'simply listen to you?', '\\option={"id":"%s","img":"images/speak.svg","label":"Talking"}\\' % LISTENING],
        RELAX_SOUNDS: ['listen', 'relaxing sounds?', '\\option={"id":"%s","img":"images/relax.svg","label":"Sounds"}\\' % RELAX_SOUNDS],
        ROCK_SCISSOR_PAPER: ['play', 'rock paper scissors?', '\\option={"id":"%s","img":"images/scissors.svg","label":"Rock Paper Scissors"}\\' % ROCK_SCISSOR_PAPER],
        STORY: ['listen', 'a story?', '\\option={"id":"%s","img":"images/story.svg","label":"Story"}\\' % STORY],
        }

MOODS_FEEDBACK = {
        PARTYMOOD: ["Cool!", "Full of energy!", "Good, I like that!"],
        HAPPY: ["Good to hear!", "Glad you feel good!", "Cool!", "Nice!"],
        CONFUSED: ["Not too sure? Let see.","A bit lost? Let see.", "That's ok.", "A bit confused? That's ok.", "Let see what we can do."],
        TIRED: ["A bit tired? Ok, let see.", "Ok, that's fine.", "Not too much energy? no worries.", "Ok, that's fine to be tired sometimes!"],
        SAD: ["Oh, sorry to hear that you feel sad", "You feel sad? Let see what we can do.", "That's ok, let see.", "Ok, thank you for letting me know."],
        ANGRY: ["Oh! You feel angry? Let see.", "You feel angry? Ok, thanks for telling me", "Ok, let see if we can calm down a little then", "That's ok to feel angry. Let see what we can do."],
        }

FINAL_MOODS_FEEDBACK = {
        PARTYMOOD: ["Cool!", "Full of energy!", "Good, I like that!", "Good to hear"],
        HAPPY: ["Good to hear!", "Glad you feel good!", "Cool!", "Nice!"],
        CONFUSED: ["Not too sure?","A bit lost?", "That's ok.", "A bit confused? That's ok."],
        TIRED: ["A bit tired?", "Still not too much energy? no worries.", "Ok, that's fine to be tired sometimes!"],
        SAD: ["Sorry to hear that you still feel sad", "Ok, thank you for letting me know."],
        ANGRY: ["Oh! You still feel angry? Maybe you should talk to an adult."],
        }

def get_dialogue(type):
    return random.choice(DIALOGUES[type])
