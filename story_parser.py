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

    def print_tree(self,node=None,level=0,prefix=""):
        import sys
        txt, actions = self.next(node)

        if txt[0].startswith("Do you want"):
            return


#        if len(actions) == 1:
#            print(str(level) + ": " + "".join(" " * level) + txt[0] + " (%s)" % self.get_audio_id(node))
 
        if len(actions) == 1:
            if level in [2,4,6,8]:
                prefix += "-%s"  % txt[0]
            if level == 9:
                sys.stdout.write(prefix + ":%s\n" % self.get_audio_id(node))
               
        for k,v in actions.items():
            self.print_tree(k, level +1, prefix)

    def get_audio_id(self, id):
        if id in self.stage_nodes:
            return self.stage_nodes[id]["audio"]
        else:
            return ""

    def get_txt(self, id):
        audio_id = self.get_audio_id(id)

        processed_filename = os.path.join(self.root_path, "assets", self.stage_nodes[id]["audio"][:-4] + ".txt")

        if os.path.exists(processed_filename):
            with open(processed_filename) as txt:
                return [l.rstrip() for l in txt.readlines()]
        else:
            logger.error("Missing Lunii story: %s." % audio_id)
            return []

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
    #story.start()
    story.print_tree()
