import copy
import importlib
import json
import os.path
import re
import traceback

import lab

# Reload the lab each time a new level is loaded.
importlib.reload(lab)


def validate_map(map_info):
    """ Given a JSON loaded map validates that it is correct. """
    expected_fields = {'width', 'height', 'rocks', 'path_corners'}
    assert expected_fields.issubset(map_info.keys()), "Missing required fields in map file!"
    if map_info.keys() - (expected_fields |
                          {'money', 'spawn_interval', 'animal_speed', 'num_allowed_unfed'}):
        print("WARNING: Unexpected information provided in map file!")


def read_map(path):
    """ Takes a JSON map file and prepares it for processing in the student's lab file. """
    with open(path, 'r') as map_file:
        game_info = json.load(map_file)
        validate_map(game_info)

        # Turn all necessary fields into their expected Python equivalents.
        game_info['path_corners'] = list(map(tuple,game_info['path_corners']))
        game_info['rocks'] = set(map(tuple, game_info['rocks']))

        # Set defaults.
        game_info['money'] = game_info.get('money', 200)
        game_info['num_allowed_unfed'] = game_info.get('num_allowed_unfed', 10)
        game_info['spawn_interval'] = game_info.get('spawn_interval', 100)
        game_info['animal_speed'] = game_info.get('animal_speed', 1)

        return game_info


def record_trace(map_file_path, input_data):
    """ Steps through a series of timesteps and reports what was rendered at each step. """
    game_info = read_map(os.path.join("resources", "maps", map_file_path))

    for input_info in input_data:
        game_info[input_info] = input_data[input_info]

    game = lab.Game(game_info)
    yield copy.deepcopy(game.render())

    # Process each timestep one at a time.
    for mouse in input_data["events"]:
        try:
            game.timestep(mouse)
        except Exception as e:
            if isinstance(e,lab.NotEnoughMoneyError):
                yield {"error": "NotEnoughMoneyError"}
                break
            else:
                raise e

        yield copy.deepcopy(game.render())


def run_replay(map_file_path, input_data):
    """ Runs a replay given the provided map file and input data. """
    return list(record_trace(map_file_path, input_data))

def run_test(input_data):
    """ Given an input test file, runs the specified replay and returns the results. """

    test_type = input_data.pop("type")
    map_file_path = input_data.pop("map")

    try:
        testfn = {
            "replay": run_replay
        }[test_type]

        return "result", testfn(map_file_path, input_data)
    except NotImplementedError:
        return "error", "Not implemented yet"
    except:
        return "error", traceback.format_exc()


##################################################
# code used by server.py -- please don't break!
##################################################

class InstrumentedGame(object):
    def __init__(self, level_name):
        # Load the game and start off at a pre-game step.
        level = read_map(os.path.join('resources', 'maps', level_name))
        self.game = lab.Game(level)
        self.window = [level['width'], level['height']]
        self.step = -1
        self.ghost_enabled = True
        self.path = level['path_corners']

        # Load all appropriate test cases and initialize state regarding the display.
        self.test_in_name = "<no .in file found>"
        self.test_out_name = "<no .out file found>"
        self.ref_in, self.ref_out = [], []
        self.load_test_output(level_name)

    def load_test_output(self, level_name):
        """ Loads test output that's provided to __init__. """
        pass # not used

    def timestep(self, ghost_mode, mouse_action):
        """ Goes through a time step of the instrumented game. """
        if ghost_mode:
            self.step += 1
            if self.step < len(self.ref_in):
                self.game.timestep(self.ref_in[self.step])
            else:
                print("No more input in {}".format(self.test_in_name))
        else:
            if isinstance(mouse_action, list):
                mouse_action = tuple(round(coord) for coord in mouse_action)
            self.game.timestep(mouse_action)

    def render(self, ghost_mode):
        """ Renders the instrumented game. """
        # Parse all output from render.
        render_output = copy.deepcopy(self.game.render())
        state = render_output['status']
        formations = render_output['formations']
        money = render_output['money']
        animals_remaining = render_output['num_allowed_remaining']

        # When ghost mode is activated adjust the formations differently.
        ref_state = None
        InstrumentedGame.add_rect_field(formations)
        if ghost_mode:
            if self.step + 1 < len(self.ref_out):
                ref_state, ref = self.ref_out[self.step + 1]
                ref = copy.deepcopy(ref)
                ref_formations = InstrumentedGame.add_rect_field(ref)
                for formation in ref_formations:
                    formation["ghost"] = True
                formations += ref_formations
            else:
                print("No more output in {}".format(self.test_out_name))
            InstrumentedGame.verify_formations(formations)

        return [state, ref_state], formations, money, animals_remaining

    @staticmethod
    def add_rect_field(formations):
        """ Add rectangle to all formations. """
        for f in formations:
            if "loc" in f:
                f["rect"] = list(f.pop("loc")) + list(f.pop("size"))
        return formations

    @staticmethod
    def verify_formations(formations):
        """ Verifies all formations in rendering output if ghost is set. """
        assert all(("rect" in f or ("loc" in f and "size" in f)) and "texture" in f for f in formations)


current_game = None

def init_game(level_name):
    """ Creates a new game. """
    global current_game
    print('loading map: "%s"' % level_name)
    current_game = InstrumentedGame(level_name)
    return current_game.ghost_enabled, current_game.window


def timestep(args):
    """ Deliver the specified action to the game, then render and return the resulting state. """
    mouse_action, ghost_mode = args
    current_game.timestep(ghost_mode, mouse_action)
    status, result, money, animals_remaining = current_game.render(ghost_mode)
    return status, result, money, current_game.path, animals_remaining, current_game.step


def render(args):
    """ Render and return the resulting game state. """
    ghost_mode = args
    status, result, money, animals_remaining = current_game.render(ghost_mode)
    return status, result, money, current_game.path, animals_remaining, current_game.step
