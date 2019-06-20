import time
import traceback
from copy import deepcopy
from importlib import reload

try:
    import lab
    reload(lab)
except ImportError:
    import solution
    lab = solution

current_game = None

def ui_new_game(d):
    global current_game
    current_game = lab.HyperMinesGame(d["dimensions"], d["bombs"])
    return

def ui_dig(d):
    coordinates = d["coordinates"]
    nd_dug = current_game.dig(coordinates)
    status = current_game.state
    return [status, nd_dug]

def ui_render(d):
    return current_game.render(d["xray"])

