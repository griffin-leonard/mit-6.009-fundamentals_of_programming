#!/usr/bin/env python3

import os
import lab
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)

class TestImage(unittest.TestCase):
    def test_load(self):
        result = lab.Image.load('test_images/centered_pixel.png')
        expected = lab.Image(11, 11,
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(result, expected)


class TestInverted(unittest.TestCase):
    def test_inverted_1(self):
        im = lab.Image.load('test_images/centered_pixel.png')
        result = im.inverted()
        expected = lab.Image(11, 11,
                             [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                              255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
        self.assertEqual(result,  expected)

    def test_inverted_2(self):
        im = lab.Image(4,1,[6, 71, 154, 212])
        result = im.inverted()
        expected = lab.Image(4,1,[249,184,101,43])
        self.assertEqual(result,  expected)
      

    def test_inverted_images(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
                result = lab.Image.load(inpfile).inverted()
                expected = lab.Image.load(expfile)
                self.assertEqual(result,  expected)


class TestFilters(unittest.TestCase):
    def test_blurred(self):
        for kernsize in (1, 3, 7):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
                    input_img = lab.Image.load(inpfile)
                    input_img_copy = lab.Image(input_img.width, input_img.height, input_img.pixels)
                    result = input_img.blurred(kernsize)
                    expected = lab.Image.load(expfile)
                    self.assertEqual(input_img, input_img_copy, "Be careful not to modify the original image!")
                    self.assertEqual(result,  expected)

    def test_sharpened(self):
        for kernsize in (1, 3, 9):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
                    input_img = lab.Image.load(inpfile)
                    input_img_copy = lab.Image(input_img.width, input_img.height, input_img.pixels)
                    result = input_img.sharpened(kernsize)
                    expected = lab.Image.load(expfile)
                    self.assertEqual(input_img, input_img_copy, "Be careful not to modify the original image!")
                    self.assertEqual(result,  expected)

    def test_edges(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
                input_img = lab.Image.load(inpfile)
                input_img_copy = lab.Image(input_img.width, input_img.height, input_img.pixels)
                result = input_img.edges()
                expected = lab.Image.load(expfile)
                self.assertEqual(input_img, input_img_copy, "Be careful not to modify the original image!")
                self.assertEqual(result,  expected)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
