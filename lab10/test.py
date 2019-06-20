#!/usr/bin/env python3
import os
import lab
import time
import pickle
import unittest
import sys
import warnings
import multiprocessing
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'test_files')
with open(os.path.join(TEST_DIRECTORY, 'results'), 'rb') as f:
        RESULTS = pickle.load(f)

class Lab10Test(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

class Test0_Streaming(Lab10Test):
    def test_hello6009world(self):
        fileContents = lab.download_file('https://6009.cat-soop.org/_static/spring19/labs/lab10/helloworld.txt')
        self.assertEqual(next(fileContents), b'Hello 6.009!\n')
        try:
            nextValues = next(fileContents)
            self.assertTrue(False, "Stream did not end")
        except StopIteration:
            self.assertTrue(True)

class Test1_Streaming(Lab10Test):
    def test_streaming(self):
        t = time.time()
        x1, x2 = RESULTS['test_streaming']
        stream = lab.download_file('http://scripts.mit.edu/~6.009/spring19/lab10/test_stream.py')
        self.assertEqual(next(stream), x1)
        self.assertEqual(next(stream), x2)
        self.assertTrue((time.time()-t) < 30, msg="Download took too long.")


class Test2_Behaviors(Lab10Test):
    def test_youbroketheinternet(self):
        stream = lab.download_file('http://scripts.mit.edu/~6.009/spring19/lab10/redir.py/0/fivedollars.wav')
        self.assertEqual(b''.join(stream), RESULTS['test_redirect'])

        with self.assertRaises(RuntimeError):
            stream = lab.download_file('http://scripts.mit.edu/~6.009/spring19/lab10/always_error.py/')
            out = b''.join(stream)
        with self.assertRaises(RuntimeError):
            stream = lab.download_file('http://nonexistent.mit.edu/hello.txt')
            out = b''.join(stream)
        with self.assertRaises(FileNotFoundError):
            stream = lab.download_file('http://hz.mit.edu/some_file_that_doesnt_exist.txt')
            out = b''.join(stream)


class Test3_Manifest(Lab10Test):
    def test_ireallylikecats(self):
        stream = lab.download_file('http://scripts.mit.edu/~6.009/spring19/lab10/redir.py/0/cat_poster.jpg.parts')
        self.assertEqual(b''.join(stream), b''.join(RESULTS['test_big']))

class Test4_InfiniteManifests(Lab10Test):
    def test_infinityandbeyond(self):
        t = time.time()

        def worker():
            stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/repeat.txt.parts')
            result = b''.join(stream)

        thr = multiprocessing.Process(target=worker)
        thr.start()
        # Wait for at most 2 seconds to load continuously for repeat.txt
        thr.join(2)
        thr.terminate()
        self.assertTrue(1.9 < abs(time.time() - t), "Infinite sequence terminates too soon")
        self.assertTrue(abs(time.time() - t) < 2.1, "Infinite sequence doesn't terminate quickly enough")


class Test5_Caching(Lab10Test):
    def test_catsaremeanttobehappy(self):
        # test that cache hits speed things up
        t = time.time()
        stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/happycat.png.parts')
        result = b''.join(stream)
        expected = 10*RESULTS['test_caching.1']
        self.assertEqual(result, expected)
        self.assertTrue(time.time() - t < 15, msg='Test took too long.')

        # test that caching isn't done unnecessarily (only where specified)
        stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/numbers.png.parts')
        result = b''.join(stream)
        count = sum(i in result for i in RESULTS['test_caching.2'])
        self.assertTrue(count > 1)

class Test6_CachingNoCache(Lab10Test):
    def test_cachecachecachecache(self):
        t = time.time()
        stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/happycat_twice.png.parts')
        result = b''.join(stream)
        expected = 3*RESULTS['test_caching.1']
        self.assertEqual(result, expected)
        completedTime = time.time() - t
        self.assertTrue(completedTime < 10, msg='Test took too long.')

        t = time.time()
        stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/happycat_twice.png.parts')
        result = b''.join(stream)
        self.assertTrue(abs(time.time() - t - completedTime) < 5, msg='Caching should be independent of download_file calls.')

class Test7_CachingCantCache(Lab10Test):
    def test_icantcachecani(self):
        stream = lab.download_file('http://mit.edu/6.009/www/spring19/lab10_examples/cachesucs.txt.parts')
        alltext = b''.join(stream).decode("utf-8").split("\n")
        self.assertTrue(len(alltext) > 5, "did not yield all times");
        time1 = alltext[0]
        time2 = alltext[1]
        timeCached = alltext[2]
        timeCached2 = alltext[3]
        time4 = alltext[4]
        time5 = alltext[5]
        self.assertTrue(time1 != time2, msg="Caching should only occur when (*) appears")
        self.assertTrue(time1 == timeCached or time2 == timeCached, msg="File was not cached")
        self.assertTrue(timeCached == timeCached2, msg="Manifest should use cache first if one file has already been cached")
        self.assertTrue(time1 == timeCached2 or time2 == timeCached2, msg="File was not cached")
        self.assertTrue(time5 != time4, msg="You should only cache if (*) appears")
        self.assertTrue(timeCached != time4, msg="If you got this error, your caching is really wrong")


def _test_sequence_gen():
    with open(os.path.join(TEST_DIRECTORY, 'test_file_sequence.input'), 'rb') as f:
        inp = f.read()
    for i in range(0, len(inp), 8192):
        yield inp[i:i+8192]
        if i == 270336:
            time.sleep(5)
    yield inp[i+8192:]

class Test8_Sequence(Lab10Test):
    def test_filesequence(self):
        gen = _test_sequence_gen()
        t = time.time()
        ix = 0
        for ix, file_ in enumerate(lab.files_from_sequence(gen)):
            self.assertEqual(file_, RESULTS['test_file_sequence'][ix],
                             msg='File %d in the sequence was not correctly extracted.' % ix)
            if ix == 4:
                self.assertTrue(time.time() - t < 0.5, msg="Yielding first 5 files took too long")

        self.assertEqual(ix, len(RESULTS['test_file_sequence'])-1,
                         msg='Incorrect number of files in file sequence.')


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
