import time
import traceback
from copy import deepcopy
from importlib import reload

try:
    import lab2d
    reload(lab2d)
except ImportError:
    import solution
    lab2d = solution

current_game = None

def ui_new_game(d):
    global current_game
    current_game = lab2d.MinesGame(d["dimensions"], d["bombs"])
    return

def ui_dig(d):
    coordinates = d["coordinates"]
    nd_dug = current_game.dig(coordinates)
    status = current_game.state
    return [status, nd_dug]

def ui_render(d):
    return current_game.render(d["xray"])