import lab, json, traceback
import copy
from importlib import reload
reload(lab) # this forces the student code to be reloaded when page is refreshed

def run_test(input_data):
  try:
    return ('ok',pack(input_data))
  except:
    return ('error',traceback.format_exc())
    

bag_list = [
  { (0,0), (1,0), (2,0) },  # vertical 3x1 bag
  { (0,0), (0,1), (0,2) },  # horizontal 1x3 bag
  { (0,0), (0,1), (1,0), (1,1) }, # square bag
  { (0,0), (1,0), (1,1) },  # L-shaped bag
  { (0,0), (0,1), (1,0), (2,0), (2,1) },  # C-shaped bag
  { (0,0), (0,1), (1,1), (2,0), (2,1) },  # reverse C-shaped bag
]


def pack(input_data):
  tent_size = tuple(input_data["tent_size"])
  missing_squares = set((r,c) for r,c in input_data["rocks"])
  max_vacancy = input_data["max_vacancy"]
  r = lab.pack(tent_size, missing_squares, bag_list, max_vacancy)
  return r

def init():
  return None

  
