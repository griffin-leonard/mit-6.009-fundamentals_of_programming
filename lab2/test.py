#!/usr/bin/env python3
import os
import lab
import json
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)


class TestTiny(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/tiny.json'
        #filename = 'resources/large.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)
    
    def test1(self):
        # Simple test, two actors who acted together
        actor1 = 1532
        actor2 = 4724
        self.assertTrue(lab.did_x_and_y_act_together(self.data, actor1, actor2))

    def test2(self):
        # Simple test, two actors who had not acted together
        actor1 = 1532
        actor2 = 1640
        self.assertFalse(lab.did_x_and_y_act_together(self.data, actor1, actor2))        

class TestActedTogether(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/small.json'
        #filename = 'resources/large.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def test_01(self):
        # Simple test, two actors who acted together
        actor1 = 4724
        actor2 = 9210
        self.assertTrue(lab.did_x_and_y_act_together(self.data, actor1, actor2))

    def test_02(self):
        # Simple test, two actors who had not acted together
        actor1 = 4724
        actor2 = 16935
        self.assertFalse(lab.did_x_and_y_act_together(self.data, actor1, actor2))

    def test_03(self):
        # Simple test, same actor
        actor1 = 4724
        actor2 = 4724
        self.assertTrue(lab.did_x_and_y_act_together(self.data, actor1, actor2))


class TestBaconNumber(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/small.json'
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def test_04(self):
        # Actors with Bacon number of 2
        n = 2
        expected = {1640, 1811, 2115, 2283, 2561, 2878, 3085, 4025, 4252, 4765,
                    6541, 9827, 11317, 14104, 16927, 16935, 19225, 33668, 66785,
                    90659, 183201, 550521, 1059002, 1059003, 1059004, 1059005,
                    1059006, 1059007, 1232763}
        result = lab.get_actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)

    def test_05(self):
        # Actors with Bacon number of 3
        n = 3
        expected = {52, 1004, 1248, 2231, 2884, 4887, 8979, 10500, 12521,
                    14792, 14886, 15412, 16937, 17488, 19119, 19207, 19363,
                    20853, 25972, 27440, 37252, 37612, 38351, 44712, 46866,
                    46867, 48576, 60062, 75429, 83390, 85096, 93138, 94976,
                    109625, 113777, 122599, 126471, 136921, 141458, 141459,
                    141460, 141461, 141495, 146634, 168638, 314092, 349956,
                    558335, 572598, 572599, 572600, 572601, 572602, 572603,
                    583590, 931399, 933600, 1086299, 1086300, 1168416, 1184797,
                    1190297, 1190298, 1190299, 1190300}
        result = lab.get_actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)


class TestActorPath(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        with open('resources/small.json', 'r') as f:
            self.db_small = json.load(f)
        with open('resources/large.json', 'r') as f:
            self.db_large = json.load(f)

    def test_06(self):
        # Actor path, large database, length of 7 (8 actors, 7 movies)
        actor_1 = 1345462
        actor_2 = 89614
        len_expected = 7
        result = lab.get_path(self.db_large, actor_1, actor_2)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], actor_1)
        self.assertEqual(result[-1], actor_2)

    def test_07(self):
        # Actor path, large database, length of 4 (5 actors, 4 movies)
        actor_1 = 100414
        actor_2 = 57082
        len_expected = 4
        result = lab.get_path(self.db_large, actor_1, actor_2)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], actor_1)
        self.assertEqual(result[-1], actor_2)

    def test_08(self):
        # Bacon path, large database, length of 7 (8 actors, 7 movies)
        actor_1 = 43011
        actor_2 = 1379833
        len_expected = 7
        result = lab.get_path(self.db_large, actor_1, actor_2)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], actor_1)
        self.assertEqual(result[-1], actor_2)

    def test_09(self):
        # Bacon path, large database, does not exist
        actor_1 = 43011
        actor_2 = 1204555
        expected = None
        result = lab.get_path(self.db_large, actor_1, actor_2)
        self.assertEqual(result, expected)


class TestBaconPath(unittest.TestCase):
    """ These tests check the actual path for validity, and to do so in a
    reasonable time requires a fast checking database. So this reveals
    both validate path and convert. It's probably better to put some
    subset of these into a web check only. Maybe to have a couple of
    tests here with a single unique path.
    """
    def setUp(self):
        """ Load actor/movie database """
        with open('resources/small.json', 'r') as f:
            self.db_small = json.load(f)
        with open('resources/large.json', 'r') as f:
            self.db_large = json.load(f)

    def test_10(self):
        # Bacon path, small database, path does not exist
        actor_id = 2876669
        expected = None
        result = lab.get_bacon_path(self.db_small, actor_id)
        self.assertEqual(result, expected)

    def test_11(self):
        # Bacon path, small database, length of 3 (4 actors, 3 movies)
        actor_id = 46866
        len_expected = 3
        result = lab.get_bacon_path(self.db_small, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_small, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_12(self):
        # Bacon path, large database, length of 2 (3 actors, 2 movies)
        actor_id = 1204
        len_expected = 2
        result = lab.get_bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_13(self):
        # Bacon path, large database, length of 4 (5 actors, 4 movies)
        actor_id = 197897
        len_expected = 4
        result = lab.get_bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_14(self):
        # Bacon path, large database, length of 6 (7 actors, 6 movies)
        actor_id = 1345462
        len_expected = 6
        result = lab.get_bacon_path(self.db_large, actor_id)
        # here, we compute the result twice, to test for mutation of the db
        result = lab.get_bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_15(self):
        # Bacon path, large database, does not exist
        actor_id = 1204555
        expected = None
        result = lab.get_bacon_path(self.db_large, actor_id)
        self.assertEqual(result, expected)


def valid_path(d, p):
    x = {frozenset(i[:-1]) for i in d}
    return all(frozenset(i) in x for i in zip(p, p[1:]))

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)

test = json.load(open('resources/names.json','r'))