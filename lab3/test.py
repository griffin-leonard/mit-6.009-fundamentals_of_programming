#!/usr/bin/env python3
import os
import lab
import json
import unittest
from copy import deepcopy

import sys
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.dirname(__file__)


class TestNewGame(unittest.TestCase):
    def test_newsmall6dgame(self):
        """ Testing new_game on a small 6-D board """
        with open("test_outputs/test_newsmall6dgame.json") as f:
            expected = json.load(f)
        with open("test_inputs/test_newsmall6dgame.json") as f:
            inputs = json.load(f)
        result = lab.HyperMinesGame(inputs["dimensions"], inputs["bombs"])
        for i in ('dimensions', 'board', 'mask', 'state'):
            self.assertEqual(getattr(result, i), expected[i])


    def test_newlarge4dgame(self):
        """ Testing new_game on a large 4-D board """
        with open("test_outputs/test_newlarge4dgame.json") as f:
            expected = json.load(f)
        with open("test_inputs/test_newlarge4dgame.json") as f:
            inputs = json.load(f)
        result = lab.HyperMinesGame(inputs["dimensions"], inputs["bombs"])
        for i in ('dimensions', 'board', 'mask', 'state'):
            self.assertEqual(getattr(result, i), expected[i])

class TestDig(unittest.TestCase):
    def test_dig(self):
        for t in ('ongoing', 'defeat'):
            with self.subTest(test=t):
                with open("test_outputs/test_dig%s.json" % t) as f:
                    expected = json.load(f)
                with open("test_inputs/test_dig%s.json" % t) as f:
                    inputs = json.load(f)
                game = from_dict(inputs["game"])
                revealed = game.dig(inputs['coordinates'])
                self.assertEqual(revealed, expected['revealed'])
                for name in expected['game']:
                    self.assertEqual(getattr(game, name), expected['game'][name])

class TestRender(unittest.TestCase):
    def test_render(self):
        with open ("test_inputs/test_render.json") as f:
            input = json.load(f)
        with open ("test_outputs/test_render.json") as f:
            output = json.load(f)

        game = from_dict(input)

        result = game.render()
        expected = output["no_xray"]
        self.assertEqual(result, expected)

        result_xray = game.render(True)
        expected_xray = output["xray"]
        self.assertEqual(result_xray, expected_xray)

class TestIntegration(unittest.TestCase):
    def _test_integration(self, n):
        with open("test_outputs/test_integration%s.json" % n) as f:
            expected = json.load(f)
        with open("test_inputs/test_integration%s.json" % n) as f:
            inputs = json.load(f)
        g = lab.HyperMinesGame(inputs['dimensions'], inputs['bombs'])
        for location, results in zip(inputs['digs'], expected):
            squares_revealed, game, rendered, rendered_xray = results
            res = g.dig(location)
            self.assertEqual(res, squares_revealed)
            for i in ('dimensions', 'board', 'mask', 'state'):
                self.assertEqual(getattr(g, i), game[i])
            self.assertEqual(g.render(), rendered)
            self.assertEqual(g.render(True), rendered_xray)

    def test_integration1(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(1)

    def test_integration2(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(2)

    def test_integration3(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(3)

class TestTiny(unittest.TestCase):
    """
    Your additional test cases for lab 3 should go here.
    """
    def test1d(self):
        game = lab.HyperMinesGame([10],[[4],[6]])
        game.dig([1])
        game.dig([6])
        expected = [' ', ' ', ' ', '1', '_', '_', '.', '_', '_', '_']
        self.assertEqual(game.render(), expected)
        
    def test2d(self):
        game = lab.HyperMinesGame([5,6],[ [3,3], [4,3], [3,4] ])
        game.dig([4,5])
        game.dig([0,0])
        expected = [[' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', '1', '2', '2', '1'], [' ', ' ', '2', '_', '_', '_'], [' ', ' ', '2', '_', '_', '1']]
        expected_xray = [[' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', ' ', ' ', ' ', ' '], [' ', ' ', '1', '2', '2', '1'], [' ', ' ', '2', '.', '.', '1'], [' ', ' ', '2', '.', '3', '1']]
        self.assertEqual(game.render(), expected)
        self.assertEqual(game.render(True), expected_xray)
        
    def test3d(self):
        game = lab.HyperMinesGame([3,3,3],[ [0,0,1] ])
        game.dig([0,0,0])
        game.dig([2,2,2])
        game.dig([0,0,2])
        expected = [[['1', '_', '1'], ['1', '1', '1'], [' ', ' ', ' ']], [['1', '1', '1'], ['1', '1', '1'], [' ', ' ', ' ']], [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]]
        self.assertEqual(game.render(), expected)
        

def from_dict(d):
    """Create a new instance of the class with attributes initialized to
    match those in the given dictionary."""
    dimensions = d['dimensions']
    bombs = []
    game = lab.HyperMinesGame(dimensions, bombs)
    for i in ('board', 'state', 'mask'):
        setattr(game, i, d[i])
    return game

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
