import lab, json, traceback, time
from importlib import reload
reload(lab)  # this forces the student code to be reloaded when page is refreshed


def run_test(input_data):
    running_time = time.time()

    # Demux to the correct function
    try:
        if input_data["function"] == "pair":
            result = lab.did_x_and_y_act_together(small_data, input_data["actor_1"], input_data["actor_2"])

        # Actors with a given bacon number
        elif input_data["function"] == "set":
            result = lab.get_actors_with_bacon_number(small_data, input_data["n"])

        # Paths in a small database
        elif input_data["function"] == "path_small":
            result = lab.get_bacon_path(small_data, input_data["actor_id"])

        # Paths in a large database
        elif input_data["function"] == "path":
            result = lab.get_bacon_path(large_data, input_data["actor_id"])

        running_time = time.time() - running_time

        return (running_time, result)
    except Exception:
        return ('error',traceback.format_exc())



# These functions are required by the UI
def better_together(d):
    return lab.did_x_and_y_act_together(small_data, d["actor_1"], d["actor_2"])


def bacon_number(d):
    return list(lab.get_actors_with_bacon_number(small_data, d["n"]))


def bacon_path(d):
    return lab.get_bacon_path(small_data, d["actor_name"])


# State that is used by both ui and test code
small_data = None
large_data = None


## Initialization
def init():
    global small_data
    global large_data
    with open('./resources/small.json', 'r') as f:
            small_data = json.load(f)
    with open('./resources/large.json', 'r') as f:
            large_data = json.load(f)

init()
