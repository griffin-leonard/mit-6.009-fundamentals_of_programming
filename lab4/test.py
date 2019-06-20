#!/usr/bin/env python3
import os
import lab
import json
import unittest
import doctest
from copy import deepcopy

import sys
sys.setrecursionlimit(100000)

TEST_DIRECTORY = os.path.dirname(__file__)

bag_list = [
  { (0,0), (1,0), (2,0) },  # vertical 3x1 bag
  { (0,0), (0,1), (0,2) },  # horizontal 1x3 bag
  { (0,0), (0,1), (1,0), (1,1) }, # square bag
  { (0,0), (1,0), (1,1) },  # L-shaped bag
  { (0,0), (0,1), (1,0), (2,0), (2,1) },  # C-shaped bag
  { (0,0), (0,1), (1,1), (2,0), (2,1) },  # reverse C-shaped bag
]

class TestPacking(unittest.TestCase):
    def test_01(self):
        """ horizontal bag in 1x3 tent, no rocks => fits """
        tent_size = (1,3)
        rocks = set()
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_02(self):
        """ vertical bag in 3x1 tent, no rocks => fits """
        tent_size = (3,1)
        rocks = set()
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_03(self):
        """ L-shaped bag in 2x2 tent, one rock => fits """
        tent_size = (2,2)
        rocks = {(0,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_04(self):
        """ Square bag in 2x2 tent, no rocks => fits """
        tent_size = (2,2)
        rocks = set()
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_05(self):
        """ 4x4 tent, no rocks => fits """
        tent_size = (4,4)
        rocks = set()
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_06(self):
        """ C-shaped bag in 3x2 tent, one rock => fits """
        tent_size = (3,2)
        rocks = {(1,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_07(self):
        """ reverse-C-shaped bag in 3x2 tent, one rock => fits """
        tent_size = (3,2)
        rocks = {(1,0)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_08(self):
        """ 7x3 tent, one rock => fits """
        tent_size = (7,3)
        rocks = {(1,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_09(self):
        """ 3x6 tent, three rocks => fits """
        tent_size = (3,6)
        rocks = {(2,1),(0,4),(1,4)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_10(self):
        """ 5x2 tent, two rocks => fits """
        tent_size = (5,2)
        rocks = {(1,0),(3,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_11(self):
        """ 5x5 tent with two rocks in the center => fits """
        tent_size = (5,5)
        rocks = {(2,2),(2,3)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_12(self):
        """ 5x5 tent with 4 rocks => fails """
        tent_size = (5,5)
        rocks = {(1,1),(1,3),(3,1),(3,3)}
        packable = False
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_13(self):
        """ 5x5 tent with three rocks => fits """
        tent_size = (5,5)
        rocks = {(1,1),(1,3),(3,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_14(self):
        """ 9x7 tent with scattered rocks => fits """
        tent_size = (9,7)
        rocks = {(0,2), (2,2), (2,4), (3,4), (7,4), (5,4), (5,5), (8,6), (7,1)}
        packable = True
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_15(self):
        """ 7x6 tent with two rocks => fails """
        tent_size = (7,6)
        rocks = {(5,5),(6,4)}
        packable = False
        extra = 0
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_16(self):
        """ 9x7 tent with scattered rocks, 1 extra space => fits """
        tent_size = (9,7)
        rocks = {(0,2), (2,2), (2,4), (3,4), (7,4), (5,4), (5,5), (8,6), (7,1), (6,3), (6,4), (6,2)}
        packable = True
        extra = 1
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_17(self):
        """ 4x4 tent with two rocks, 2 extra spaces => fits """
        tent_size = (4,4)
        rocks = {(3,2),(2,3)}
        packable = True
        extra = 2
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_18(self):
        """ 4x4 tent with two rocks, 1 extra space => fails """
        tent_size = (4,4)
        rocks = {(3,2),(2,3)}
        packable = False
        extra = 1
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_19(self):
        """ 4x4 tent with two rocks, 2 extra spaces => fits """
        tent_size = (4,4)
        rocks = {(0,1),(1,0)}
        packable = True
        extra = 2
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def test_20(self):
        """ 4x4 tent with two rocks, 1 extra space => fails """
        tent_size = (4,4)
        rocks = {(0,1),(1,0)}
        packable = False
        extra = 1
        self.validate_result(tent_size, rocks, packable, extra, lab.pack(tent_size, rocks, bag_list, extra))

    def validate_result(self, tent_size, covered, packable, extra, result):
        if not packable:
            self.assertIsNone(result, msg="Proposed a packing for an impossible tent!")
            print('OK', flush=True)
            return
        self.assertIsNotNone(result, msg="Failed to find a packing solution where one exists.")
        self.assertIsInstance(result, list)

        (rows,cols) = tent_size
        tent = [[0 for c in range(cols)] for r in range(rows)]
        for r,c in covered: tent[r][c] = 'r'
        for bag in result:
            btype = bag.get("shape")
            self.assertIsNotNone(btype, msg="Person dictionary missing 'shape' key.")
            self.assertIsInstance(btype, int, msg="Person shape not an int.")
            self.assertTrue(btype >= 0 and btype < len(bag_list), msg="Person shape out of range.")

            anchor = bag.get("anchor")
            self.assertIsNotNone(anchor, msg="Person dictionary missing 'anchor' key.")
            self.assertIsInstance(anchor, tuple, msg="Person anchor not a tuple.")
            self.assertEqual(2, len(anchor), msg="Person anchor not length 2.")
            for i in [0, 1]:
                self.assertIsInstance(anchor[i], int, msg="Person anchor not of the form (int,int).")
            self.assertTrue(anchor[0] >= 0 and anchor[0] < rows, msg="Person anchor row out of range.")
            self.assertTrue(anchor[1] >= 0 and anchor[1] < cols, msg="Person anchor column out of range.")
                
            squares = [(anchor[0] + r, anchor[1] + c) for r,c in bag_list[btype]]
            for (r,c) in squares:
                self.assertTrue(r >= 0 and r < rows and c >= 0 and c < cols,
                                msg="One of your sleeping bags is not in the tent: "+str(bag))
                self.assertNotEqual("r", tent[r][c], msg="Found a sleeping bag over a rock: "+str(bag))
                self.assertNotEqual("b", tent[r][c], msg="Found overlapping sleeping bag: "+str(bag))
                tent[r][c] = "b" #mark bag

        all_filled = sum(tent[r][c] == 0 for c in range(cols) for r in range(rows)) <= extra
        self.assertTrue(all_filled, msg="Oops, there's still an empty square")
        print('OK', flush=True)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
