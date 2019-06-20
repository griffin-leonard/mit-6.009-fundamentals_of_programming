#!/usr/bin/env python3
import wrapper
import os.path
import unittest
import json
import traceback
from copy import deepcopy


TEST_DIRECTORY = os.path.dirname(__file__)

################################################################################
################################################################################
# Tests

class Test_1_KeeperPlacement(unittest.TestCase):

    def test_01(self): 
        # Place keeper (valid), enough money
        # using resources/maps/zoo4-left-to-bottom.json
        verify_case('1-1a')

        # Place keeper on path
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-1b')

    def test_02(self): 

        # Place keeper on rock
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-2a')

        # Place keeper, not enough money
        # using resources/maps/zoo5-corner-to-corner.json
        verify_case('1-2b')

    def test_03(self): 
        # Make edge of keeper intersect with edge of path
        # using resources/maps/zoo7-ugly-path.json
        verify_case('1-3a')

        # Place one of each keeper type
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-3b')

    def test_04(self): 
        # event sequence: keeper, None, loc
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-4a')

        # place edge/corner of keeper on rock (but not anchor of keeper)
        # using resources/maps/zoo7-ugly-path.json
        verify_case('1-4b')

    def test_05(self): 
        # Place 2 keepers, enough money for first, but not for second
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-5a')

        # Place keeper on path; starts will null mouse
        # using resources/maps/zoo2-horizontal-path.json
        verify_case('1-5b')


class Test_2_AnimalMovement(unittest.TestCase):

    # spawn interval 1, horizontal path
    # using resources/maps/zoo2-horizontal-path.json
    def test_01(self): verify_case('2-1')

    # spawn interval 4, windy path, make a turn during a timestep
    # using resources/maps/zoo5-corner-to-corner.json
    def test_02(self): verify_case('2-2')

    # highspeed animal, windy path, makes two turns during a timestep (sharp turn)
    # using resources/maps/zoo6-many-turns.json
    def test_03(self): verify_case('2-3')

    # spawn interval 2, turn exactly on corner, and then one off of corner on a next turn
    # using resources/maps/zoo7-ugly-path.json
    def test_04(self): verify_case('2-4')

    # defeat condition, let animals go all the way through
    # using resources/maps/zoo1-tiny.json
    def test_05(self): verify_case('2-5')


class Test_3_Feeding(unittest.TestCase):

    # 1 keeper inrange, 1 animal, vertical path
    # using resources/maps/zoo3-vertical-path.json
    def test_01(self): verify_case('3-1')

    # 1 keeper inrange, 1 animal, food aims at animal through a turn/corner
    # using resources/maps/zoo5-corner-to-corner.json
    def test_02(self): verify_case('3-2')

    # multiple keepers inrange, multiple animals, simple path
    # using resources/maps/zoo3-vertical-path.json
    def test_03(self): verify_case('3-3')

    # multiple keepers inrange, multiple animals, windy path
    # using resources/maps/zoo7-ugly-path.json
    def test_04(self): verify_case('3-4')

    # one keeper inrange, multiple animals, animals get through
    # using resources/maps/zoo3-vertical-path.json
    def test_05(self): verify_case('3-5')


# End of test cases.
################################################################################
################################################################################


################################################################################
################################################################################
# Test setup from here on.

def almost_equal(result, expected, delta=.001):
    """ Determines if two unique_order tuples are truly equal 
    (within a delta for numbers). 
    """
    for i, j in zip(result, expected):
        if isinstance(i, (int, float)) and abs(i-j) > delta:
            return False
        elif isinstance(i, str) and i != j:
            return False
    return True

def compare_formations(result_formations, expected_formations):
    """ Hashes the formations for comparison with == """
    if len(result_formations) != len(expected_formations):
        return False
    result_formations_list = unique_order(result_formations)
    expected_formations_list = unique_order(expected_formations)
    return all((almost_equal(result, expected)
                for result, expected in zip(result_formations_list, expected_formations_list)))

def unique_order(formations):
    return sorted([(*tuple(form["loc"]), *tuple(form["size"]), form["texture"]) for form in formations])

def pretty_str(formations):
    sorted_f = sorted([{"loc": tuple(form["loc"]), 
                        "size": tuple(form["size"]), 
                        "texture": form["texture"]}
                          for form in formations], 
                          key=lambda f: (*f["loc"], *f["size"], f["texture"]))
    prettied = "\n"
    for f in sorted_f:
        prettied += str(f)
        prettied += "\n"
    return prettied

def verify_render(result, expected):
    assert set(result) == set(expected)

    # Check for an in-game exception
    if "error" in result:
        return result["error"] == expected["error"]

    if not compare_formations(result['formations'], expected['formations']):
        raise AssertionError("\nIncorrect set of formations:\nExpected: \n" 
                                + pretty_str(expected['formations']) 
                                + "\nGot:\n" 
                                + pretty_str(result['formations']))

    for attr in ('money', 'status', 'num_allowed_remaining'):
        assert result[attr] == expected[attr], "\nIncorrect \"{}\" value:\nExpected {}.\nGot {}.".format(attr, expected[attr], result[attr])

    return True

def verify_replay(result_trace, expected_trace):
    assert len(result_trace) == len(expected_trace)
    for result, expected in zip(result_trace, expected_trace):
        assert verify_render(result, expected)

def verify(result, input_data, gold):
    restype, result = result

    if restype == "error":
        return False, "raised an error: {}".format(result)

    try:
        test_type = input_data["type"]
        verifn = {"replay": verify_replay}[test_type]
        errmsg = verifn(result, gold)

        if errmsg is not None:
            return False, errmsg
        else:
            return True, "is correct. Hooray!"
    except:
        traceback.print_exc()
        return False, "crashed :(. Stack trace is printed above so you can debug."

def read_input_file(cname):
    with open(os.path.join('cases', cname+'.in'), 'r') as f:
        indata = json.loads(f.read())
    assert {"type", "map", "events", "money", "num_allowed_unfed",
            "spawn_interval", "animal_speed"}.issubset(set(indata.keys()))
    indata["events"] = [tuple(event) if isinstance(event, list) else event for event in indata["events"]]
    return indata

def read_output_file(cname):
    with open(os.path.join('cases', cname+'.out'), 'r') as f:
        outdata = json.loads(f.read())

    # If there's no exception, compare the render outputs
    for render_dict in outdata:
        if "error" in render_dict:
            continue
        for formation in render_dict["formations"]:
            formation["loc"] = tuple(formation["loc"])
            formation["size"] = tuple(formation["size"])

    return outdata

def verify_case(cname):
    # read .in and .out files from cases
    indata = read_input_file(cname)
    outdata = read_output_file(cname)

    # first run the test
    result = wrapper.run_test(deepcopy(indata))

    # then run the verifier
    vresult, vmsg = verify(result, deepcopy(indata), deepcopy(outdata))

    # if failure, alert the test system
    if not vresult:
        raise AssertionError(vmsg)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
