import logging
logger = logging.getLogger("story_parser")

import json
import os.path

class Story:

    root_path = ""
    root = None

    stage_nodes = {}
    action_nodes = {}

    def __init__(self, story_json):
        

        story = None

        self.root_path = os.path.dirname(story_json)

        with open(story_json) as json_file:
            story = json.load(json_file)

        for n in story["stageNodes"]:
            self.stage_nodes[n["uuid"]] = n

        for n in story["actionNodes"]:
            self.action_nodes[n["id"]] = n

        for id, n in self.stage_nodes.items():
            if "squareOne" in n:
                self.root = id

    def start(self):
        self.do_next_step(self.root)


    def get_txt(self, id):
        audio_id = self.stage_nodes[id]["audio"]

        FALLBACK_STORY = "d784b0756937184c7cd39e0441ee6638906ca975"

        fallback_filename = os.path.join(self.root_path, "assets", FALLBACK_STORY + ".txt")
        processed_filename = os.path.join(self.root_path, "assets", self.stage_nodes[id]["audio"][:-4] + ".txt")

        if os.path.exists(processed_filename):
            with open(processed_filename) as txt:
                return txt.readlines()
        else:
            logger.warning("Unprocessed Lunii story: %s. Using fallback story." % audio_id)
            with open(fallback_filename) as txt:
                return txt.readlines()

    def next(self, id=None):


        if not id:
            id = self.root

        txt = self.get_txt(id)

        action = self.stage_nodes[id]["okTransition"]["actionNode"]

        actions = self.action_nodes[action]["options"]

        if len(actions) == 1:
            return txt, {actions[0]: {"img":"check-circle.svg", "label":""}}
        else:
            actions = {id: {"img": self.stage_nodes[id]["image"][:-4] + ".png", "label":self.get_txt(id)[0]} for id in actions}
            return txt, actions


    def do_next_step(self, id):

        txt, actions = self.next(id)

        audio_id = self.stage_nodes[id]["audio"]

        print("\n===================================== %s" % audio_id)
        print(" ".join(txt))

        actions_ids = list(actions.keys())
        if len(actions_ids) == 1:
            raw_input("(press Enter to continue)")
            self.do_next_step(actions_ids[0])
        else:
            for idx, a in enumerate(actions_ids):
                print("%s. %s" % (idx + 1, self.get_line(a)))

            choice = int(input("What option do you want? Press a number followed by Enter."))

            self.do_next_step(actions_ids[choice - 1])


if __name__ == "__main__":
    story = Story("static/stories/susanne-and-ben/story.json")
    story.start()
