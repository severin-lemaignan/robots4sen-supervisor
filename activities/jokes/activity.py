import logging
logger = logging.getLogger("robots.activities.jokes")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

JOKES_LIST = [
            "How do you make a sausage roll?\\pau=1500\\^startTag(down)Roll it down a hill!",
            "Why did the teddy bear say no to dessert?\\pau=1700\\^startTag(down)Because she was stuffed.",
            "What did the left eye say to the right eye?\\pau=1600\\Between us, something smells!",
            "What is brown, hairy and wears sunglasses?\\pau=1400\\A coconut on vacation.",
            "When you look for something, why is it always in the last place you look?\\pau=1400\\Because when you find it, you stop looking.",
            "Why did the kid cross the playground?\\pau=1400\\To get to the other slide.",
            "Why was 6 afraid of 7?\\pau=1800\\Because 7 8 9.",
            "What is a witch's favorite subject in school?\\pau=1300\\Spelling!",
            "How do you make a lemon drop?\\pau=1600\\Just let it fall.",
            "What kind of water cannot freeze?\\pau=1600\\Hot water.",
            "What kind of tree fits in your hand?\\pau=1500\\A palm tree!",
            "What did the little corn say to the mama corn?\\pau=1600\\Where is pop corn?",
            "Where would you find an elephant?\\pau=1500\\The same place you lost her!",
            "What falls in winter but never gets hurt?\\pau=1500\\Snow!",
            "What building in London has the most stories?\\pau=1600\\The public library!",
            "What did one volcano say to the other?\\pau=1400\\I lava you!",
            "How do we know that the ocean is friendly?\\pau=1600\\It waves!",
            "How does the moon cut his hair?\\pau=1600\\Eclipse it.",
            "How do you get a squirrel to like you?\\pau=1700\\Act like a nut!",
            "How can you tell a vampire has a cold?\\pau=1700\\She starts coffin.",
            "What did the left eye say to the right eye?\\pau=1700\\Between us, something smells!",
            "What's worse than finding a worm in your apple?\\pau=1600\\Finding half a worm.",
            "What is a computer's favorite snack?\\pau=1400\\Computer chips!!",
            "Why don't elephants chew gum?\\pau=1600\\They do, just not in public.",
            "What did the banana say to the dog?\\pau=1500\\Nothing. Bananas can't talk.",
            "What time is it when the clock strikes 13?\\pau=1600\\Time to get a new clock.",
            "What do you call a boomerang that won't come back?\\pau=1700\\A stick.",
            "What do you think of that new dinner on the moon?\\pau=1400\\Food was good, but there really wasn't much atmosphere.",
            "Why did the dinosaur cross the road?\\pau=1800\\Because the chicken wasn't born yet.",
            "Why can't Elsa have a balloon?\\pau=1600\\Because she will let it go.",
            "How do you make an octopus laugh?\\pau=1600\\With ten-tickles!",
            "How do you make a tissue dance?\\pau=1600\\You put a little boogie in it.",
            "What did the nose say to the finger?\\pau=1600\\Quit picking on me!",
            "Why did the kid bring a ladder to school?\\pau=1600\\Because she wanted to go to high school.",
            "What do elves learn in school?\\pau=1600\\The elf abet.",
            "What do you call a dog magician?\\pau=1600\\A labracadabrador.",
            "What gets wetter the more it dries?\\pau=1600\\A towel.",
            "Why did the banana go to the doctor?\\pau=1600\\Because it wasn't peeling well.",
            "What stays in the corner yet can travel all over the world?\\pau=1600\\A stamp.",
            "What do you call a funny mountain?\\pau=1600\\Hill arious.",
            "Why are ghosts bad liars?\\pau=1600\\Because you can see right through them.",
            "Why do bees have sticky hair?\\pau=1600\\Because they use a honeycomb.",
            "Where do fish keep their money?\\pau=1600\\In the River Bank!",
            "Why was the computer cold?\\pau=1600\\It had a virus. ",
            "Why did the invisible man turn down the job offer?\\pau=1600\\Because he couldn't see himself doing it.",
            "Who keeps the ocean clean?\\pau=1600\\The mer\\pau=200\\maid.",
            "Why didn't the orange win the race?\\pau=1600\\It ran out of juice.",
            "What do you call an old snowman?\\pau=1500\\Water.",
            "What do you call a sleeping bull?\\pau=1700\\A bulldozer! ",
            "What part of the fish weighs the most? \\pau=1600\\The scales. ",
            "What do ghosts like to eat in the summer?\\pau=1400\\I Scream.",
            "Why did the teacher wear sunglasses to school?\\pau=1600\\Because her students were so bright. ",
            "Why do birds fly?\\pau=1800\\It's faster than walking. ",
            "Can February March?\\pau=1400\\No, but April May. ",
            "Why do you never see elephants hiding in trees?\\pau=1500\\Because they're so good at it!",
            "What do you call a fly with no wings?\\pau=1500\\A walk.",
            "How do squids get to school?\\pau=1600\\They take an octobus.",
            "What word starts with the letter t, ends with the letter t, and has t in it?\\pau=1600\\A teapot!",        ]

class JokesActivity(Activity):

    type = JOKES

    def __init__(self):
        super(JokesActivity, self).__init__()

    def start(self, robot, cmd_queue):
        super(JokesActivity, self).start(robot, cmd_queue)

        self.jokes = random.sample(JOKES_LIST, random.randint(2,3))

    def run(self):

        self.robot.tablet.clearAll()
        self.robot.say(get_dialogue("jokes_start")).wait()
        yield RUNNING

        self.robot.tablet.addCancelBtn()

        while self.jokes:
            joke = self.jokes.pop() + "^runTag(happy)"
            self.robot.say(joke).wait()
            yield RUNNING

            if self.jokes:
                self.robot.say(get_dialogue("jokes_inbetween")).wait()
                yield RUNNING

        self.robot.say(get_dialogue("jokes_end")).wait()

    def on_no_one_engaged(self, evt):
        self.robot.say(get_dialogue("jokes_no_one_left")).wait()
        return super(JokesActivity, self).on_no_one_engaged(evt)

activity = JokesActivity()

def get_activity():
    return activity

