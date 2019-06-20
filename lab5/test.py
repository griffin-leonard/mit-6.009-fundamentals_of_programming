#!/usr/bin/env python3
import os.path
import lab
import json
import unittest
import pickle

import sys
sys.setrecursionlimit(10000)

TEST_DIRECTORY = os.path.dirname(__file__)

# convert trie into a dictionary...
def dictify(t):
    out = {'value': t.value, 'children': {}}
    for ch, child in t.children.items():
        out['children'][ch] = dictify(child)
    return out

# ...and back
def from_dict(d):
    t = lab.Trie()
    for k, v in d.items():
        t.set(k, v)
    return t

# make sure the keys are not explicitly stored in any node
def any_key_stored(trie, keys):
    keys = [tuple(k) for k in keys]
    for i in dir(trie):
        try:
            val = tuple(getattr(trie, i))
        except:
            continue
        for j in keys:
            if j == val:
                return repr(i), repr(j)
    for child in trie.children.values():
        key_stored = any_key_stored(child, keys)
        if key_stored:
            return key_stored
    return None

# read in expected result
def read_expected(fname):
    with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', fname), 'rb') as f:
        return pickle.load(f)

class Test_1_Trie(unittest.TestCase):
    def test_01_set(self):
        trie = lab.Trie()
        trie.set('cat', 'kitten')
        trie.set('car', 'tricycle')
        trie.set('carpet', 'rug')
        expect = read_expected('1.pickle')
        self.assertTrue(dictify(trie) == expect, msg="Your trie is incorrect.")
        self.assertEqual(any_key_stored(trie, ('cat', 'car', 'carpet')), None)

        t = lab.Trie()
        t.set('a', 1)
        t.set('an', 1)
        t.set('ant', 1)
        t.set('anteater', 1)
        t.set('ants', 1)
        t.set('a', 2)
        t.set('an', 2)
        t.set('a', 3)
        expect = read_expected('2.pickle')
        self.assertTrue(dictify(t) == expect, msg="Your trie is incorrect.")
        self.assertEqual(any_key_stored(t, ('an', 'ant', 'anteater', 'ants')), None)
        with self.assertRaises(TypeError):
            t.set((1, 2, 3), 20)

        t = lab.Trie()
        t.set('man', 'person')
        t.set('mat', 'object')
        t.set('mattress', 'thing you sleep on')
        t.set('map', 'pam')
        t.set('me', 'you')
        t.set('met', 'tem')
        t.set('a', '?')
        t.set('map', -1000)
        expect = read_expected('3.pickle')
        self.assertTrue(dictify(t) == expect, msg="Your trie is incorrect.")
        self.assertEqual(any_key_stored(t, ('man', 'mat', 'mattress', 'map', 'me', 'met', 'map')), None)
        with self.assertRaises(TypeError):
            t.set(('something',), 'pam')

    def test_02_get(self):
        d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39}
        t = from_dict(d)
        self.assertEqual(dictify(t), read_expected('person.pickle'))
        self.assertTrue(all(t.get(k) == d[k] for k in d))
        self.assertEqual(any_key_stored(t, tuple(d)), None)

        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('car.pickle'))
        self.assertTrue(all(t.get(k) == c[k] for k in c))
        self.assertEqual(any_key_stored(t, tuple(c)), None)
        for i in ('these', 'keys', 'dont', 'exist'):
            with self.assertRaises(KeyError):
                x = t.get(i)
        with self.assertRaises(TypeError):
            x = t.get((1, 2, 3))

    def test_03_contains(self):
        d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39}
        t = from_dict(d)
        self.assertEqual(dictify(t), read_expected('person.pickle'))
        self.assertTrue(all(t.contains(i) for i in d))

        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('car.pickle'))
        self.assertTrue(all(t.contains(i) for i in c))
        badkeys = ('these', 'keys', 'dont', 'exist', 'm', 'ma', 'mak', 'mo',
                   'mod', 'mode', 'ye', 'yea', 'y', '', 'car.pickle')
        self.assertFalse(any(t.contains(i) for i in badkeys))

    def test_04_items(self):
        t = lab.Trie()
        t.set('man', 'person')
        t.set('mat', 'object')
        t.set('mattress', 'thing you sleep on')
        t.set('map', 'pam')
        t.set('me', 'you')
        t.set('met', 'tem')
        t.set('a', '?')
        t.set('map', -1000)
        l = sorted(t.items())
        expected = [('a', '?'), ('man', 'person'), ('map', -1000), ('mat', 'object'),
                    ('mattress', 'thing you sleep on'), ('me', 'you'), ('met', 'tem')]
        self.assertEqual(l, expected)

    def test_05_delete(self):
        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('car.pickle'))
        t.delete('color')
        self.assertEqual(set(t.items()), set(c.items()) - {('color', 'beige')})
        t.set('color', 'silver')  # new paint job
        for i in t.items():
            if i[0] != 'color':
                self.assertIn(i, c.items())
            else:
                self.assertEqual(i[1], 'silver')

        t = lab.Trie()
        t.set('man', 'person')
        t.set('mat', 'object')
        t.set('mattress', 'thing you sleep on')
        t.set('map', 'pam')
        t.set('me', 'you')
        t.set('met', 'tem')
        t.set('a', '?')
        t.set('map', -1000)
        l = sorted(t.items())
        expected = [('a', '?'), ('man', 'person'), ('map', -1000), ('mat', 'object'),
                    ('mattress', 'thing you sleep on'), ('me', 'you'), ('met', 'tem')]
        self.assertEqual(l, expected)
        t.delete('mat')
        l = sorted(t.items())
        expected = [('a', '?'), ('man', 'person'), ('map', -1000),
                    ('mattress', 'thing you sleep on'), ('me', 'you'), ('met', 'tem')]
        self.assertEqual(l, expected)




class Test_2_TupleTrie(unittest.TestCase):
    def test_01_set(self):
        trie = lab.Trie()
        trie.set((1, 2, 3), 'kitten')
        trie.set((1, 2, 0), 'tricycle')
        trie.set((1, 2, 0, 1), 'rug')
        expect = read_expected('4.pickle')
        self.assertTrue(dictify(trie) == expect, msg="Your trie is incorrect.")
        self.assertEqual(any_key_stored(trie, ((1, 2, 3), (1, 2, 0), (1, 2, 0, 1))), None)

        t = lab.Trie()
        t.set((7, 8, 9), 1)
        t.set((7, 8, 9, 'hello'), 1)
        t.set((7, 8, 9, 'hello', (1, 2)), 1)
        t.set((1, ), 1)
        t.set((7, ), 1)
        t.set((7, 8, 9), 2)
        t.set((-1, -2, -3), 2)
        t.set(('a', ), 3)
        expect = read_expected('5.pickle')
        self.assertTrue(dictify(t) == expect, msg="Your trie is incorrect.")
        self.assertEqual(any_key_stored(t, ((7, 8, 9), (7, 8, 9, 'hello'),
                                               (7, 8, 9, 'hello', (1, 2)), (1, ),
                                               (7, ), (-1, -2, -3), ('a', ))), None)

    def test_02_get(self):
        d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39}
        d = {tuple(k): v for k,v in d.items()}
        t = from_dict(d)
        self.assertEqual(dictify(t), read_expected('tuple_person.pickle'))
        self.assertTrue(all(t.get(k) == d[k] for k in d))
        self.assertEqual(any_key_stored(t, tuple(d)), None)
        with self.assertRaises(TypeError):
            t.set('string', 20)

        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        c = {tuple(k): v for k,v in c.items()}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('tuple_car.pickle'))
        self.assertTrue(all(t.get(k) == c[k] for k in c))
        self.assertEqual(any_key_stored(t, tuple(c)), None)
        for i in ('these', 'keys', 'dont', 'exist'):
            with self.assertRaises(KeyError):
                x = t.get(tuple(i))
        with self.assertRaises(TypeError):
            t.set(('yarn', 'twine', 'thread')[0], 20)

    def test_03_contains(self):
        d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39}
        d = {tuple(k): v for k,v in d.items()}
        t = from_dict(d)
        self.assertEqual(dictify(t), read_expected('tuple_person.pickle'))
        self.assertTrue(all(t.contains(i) for i in d))
        with self.assertRaises(TypeError):
            x = t.get('string')

        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        c = {tuple(k): v for k,v in c.items()}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('tuple_car.pickle'))
        self.assertTrue(all(t.contains(i) for i in c))
        badkeys = ('these', 'keys', 'dont', 'exist', 'm', 'ma', 'mak', 'mo',
                   'mod', 'mode', 'ye', 'yea', 'y', '', 'car.pickle')
        self.assertFalse(any(t.contains(tuple(i)) for i in badkeys))
        with self.assertRaises(TypeError):
            x = t.get(('yarn', 'twine', 'thread')[0])

    def test_04_items(self):
        t = lab.Trie()
        t.set((7, 8, 9), 1)
        t.set((7, 8, 9, 'hello'), 1)
        t.set((7, 8, 9, 'hello', (1, 2)), 1)
        t.set((1, ), 1)
        t.set((7, ), 1)
        t.set((7, 8, 9), 2)
        t.set((-1, -2, -3), 2)
        t.set((2, ), 3)
        l = sorted(t.items())
        expected = [((-1, -2, -3), 2), ((1,), 1), ((2,), 3), ((7,), 1),
                    ((7, 8, 9), 2), ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
        self.assertEqual(l, expected)

    def test_05_delete(self):
        c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
        c = {tuple(k): v for k,v in c.items()}
        t = from_dict(c)
        self.assertEqual(dictify(t), read_expected('tuple_car.pickle'))
        t.delete(tuple('color'))
        self.assertEqual(set(t.items()), set(c.items()) - {(tuple('color'), 'beige')})
        t.set(tuple('color'), 'silver')  # new paint job
        for i in t.items():
            if i[0] != tuple('color'):
                self.assertIn(i, c.items())
            else:
                self.assertEqual(i[1], 'silver')

        t = lab.Trie()
        t.set((7, 8, 9), 1)
        t.set((7, 8, 9, 'hello'), 1)
        t.set((7, 8, 9, 'hello', (1, 2)), 1)
        t.set((1, ), 1)
        t.set((7, ), 1)
        t.set((7, 8, 9), 2)
        t.set((-1, -2, -3), 2)
        t.set((2, ), 3)
        l = sorted(t.items())
        expected = [((-1, -2, -3), 2), ((1,), 1), ((2,), 3), ((7,), 1),
                    ((7, 8, 9), 2), ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
        self.assertEqual(l, expected)
        t.delete((7, 8, 9))
        l = sorted(t.items())
        expected = [((-1, -2, -3), 2), ((1,), 1), ((2,), 3), ((7,), 1),
                    ((7, 8, 9, 'hello'), 1), ((7, 8, 9, 'hello', (1, 2)), 1)]
        self.assertEqual(l, expected)


class Test_3_Corpora(unittest.TestCase):
    def test_01_word_trie(self):
        # small test
        l = lab.make_word_trie('toonces was a cat who could drive a car very fast until he crashed.')
        expected = read_expected('6.pickle')
        self.assertEqual(dictify(l), expected)

        l = lab.make_word_trie('a man at the market murmered that he had met a mermaid. '
                               'mark didnt believe the man had met a mermaid.')
        expected = read_expected('7.pickle')
        self.assertEqual(dictify(l), expected)

        l = lab.make_word_trie('what happened to the cat who had eaten the ball of yarn?  she had mittens!')
        expected = read_expected('8.pickle')
        self.assertEqual(dictify(l), expected)


    def test_02_phrase_trie(self):
        # small test
        l = lab.make_phrase_trie('toonces was a cat who could drive a car very fast until he crashed.')
        expected = read_expected('9.pickle')
        self.assertEqual(dictify(l), expected)

        l = lab.make_phrase_trie('a man at the market murmered that he had met a mermaid. '
                                 'i dont believe that he had met a mermaid.')
        expected = read_expected('10.pickle')
        self.assertEqual(dictify(l), expected)

        l = lab.make_phrase_trie(('What happened to the cat who ate the ball of yarn?  She had mittens!  '
                                   'What happened to the frog who was double parked?  He got toad!  '
                                   'What happened yesterday?  I dont remember.'))
        expected = read_expected('11.pickle')
        self.assertEqual(dictify(l), expected)


    def test_03_big_corpora(self):
        for bigtext in ('holmes', 'earnest', 'frankenstein'):
            with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', '%s.txt' % bigtext), encoding='utf-8') as f:
                text = f.read()
                w = lab.make_word_trie(text)
                p = lab.make_phrase_trie(text)

                w_e = read_expected('%s_words.pickle' % bigtext)
                p_e = read_expected('%s_phrases.pickle' % bigtext)

                self.assertEqual(dictify(w), w_e, 'word trie does not match for '+bigtext)
                self.assertEqual(dictify(p), p_e, 'phrase trie does not match for '+bigtext)


class Test_4_AutoComplete(unittest.TestCase):
    def test_01_autocomplete(self):
        # Autocomplete on simple trie with less than N valid words
        trie = lab.make_word_trie("cat car carpet")
        result = lab.autocomplete(trie, 'car', 3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["car", "carpet"]
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")

        trie = lab.make_word_trie("a an ant anteater a an ant a")
        result = lab.autocomplete(trie, 'a', 2)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect_one_of = [["a","an"],["a","ant"]]
        self.assertIn(result,expect_one_of,msg="incorrect result from autocomplete.")

        trie = lab.make_word_trie("man mat mattress map me met a man a a a map man met")
        result = lab.autocomplete(trie, 'm', 3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["man","map","met"]
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")

        trie = lab.make_word_trie("hello hell history")
        result = lab.autocomplete(trie, 'help', 3)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        expect = []
        self.assertEqual(result,expect,msg="incorrect result from autocomplete.")
        with self.assertRaises(TypeError):
            result = lab.autocomplete(trie, ('tuple', ), None)

    def test_02_big_autocomplete(self):
        nums = {'t': [0, 1, 25, None],
                'th': [0, 1, 21, None],
                'the': [0, 5, 21, None],
                'thes': [0, 1, 21, None]}
        with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
            text = f.read()
        w = lab.make_word_trie(text)
        for i in sorted(nums):
            for n in nums[i]:
                result = lab.autocomplete(w, i, n)
                expected = read_expected('frank_autocomplete_%s_%s.pickle' % (i, n))
                self.assertEqual(len(result), len(expected), msg=('missing' if len(result) < len(expected)\
                    else 'too many') + ' autocomplete results for ' + repr(i) + ' with macount = ' + str(n))
                self.assertEqual(set(result), set(expected), msg='autocomplete included ' + repr(set(result) - set(expected))\
                    + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n))
        with self.assertRaises(TypeError):
            result = lab.autocomplete(w, ('tuple', ), None)

    def test_03_big_autocomplete_2(self):
        with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
            text = f.read()
        w = lab.make_word_trie(text)
        the_word = 'accompany'
        for ix in range(len(the_word)+1):
            test = the_word[:ix]
            result = lab.autocomplete(w, test)
            expected = read_expected('frank_autocomplete_%s_%s.pickle' % (test, None))
            self.assertEqual(len(result), len(expected), msg=('missing' if len(result) < len(expected)\
                else 'too many') + ' autocomplete results for ' + repr(test) + ' with maxcount = None')
            self.assertEqual(set(result), set(expected), msg='autocomplete included ' + repr(set(result) - set(expected))\
                + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(test) + ' with maxcount = None')
        with self.assertRaises(TypeError):
            result = lab.autocomplete(w, ('tuple', ), None)


    def test_04_big_phrase_autocomplete(self):
        nums = {('i', ): [0, 1, 2, 5, 11, None],
                ('i', 'do'): [0, 1, 2, 5, 8, None],
                ('i', 'do', 'not', 'like', 'them'): [0, 1, 2, 4, 100, None],
                ('i', 'do', 'not', 'like', 'them', 'here'): [0, 1, 2, 100, None]}
        with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', 'seuss.txt'), encoding='utf-8') as f:
            text = f.read()
        p = lab.make_phrase_trie(text)
        for i in sorted(nums):
            for n in nums[i]:
                result = lab.autocomplete(p, i, n)
                expected = read_expected('seuss_autocomplete_%s_%s.pickle' % (len(i), n))
                self.assertEqual(len(result), len(expected), msg=('missing' if len(result) < len(expected)\
                    else 'too many') + ' autocomplete results for ' + repr(i) + ' with macount = ' + str(n))
                self.assertEqual(set(result), set(expected), msg='autocomplete included ' + repr(set(result) - set(expected))\
                    + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n))

        with self.assertRaises(TypeError):
            result = lab.autocomplete(p, 'string', None)
            
    #my test cases
    def test_tiny1(self):
        trie = lab.make_word_trie("bat bat bark bar")
        
        result = lab.autocomplete(trie, 'ba', 1)
        expect = ['bat']
        self.assertEqual(result,expect)
        
        result = sorted(lab.autocomplete(trie, 'ba', 2))
        expect = sorted(['bat','bar'])
        self.assertEqual(result,expect)
    
        result = lab.autocomplete(trie, 'c', 2)
        expect = []
        self.assertEqual(result,expect)
        
        result = lab.autocomplete(trie, 'b', None)
        expect = ['bat','bar','bark']
        self.assertEqual(result,expect)
    
    def test_tiny2(self):
        trie = lab.make_word_trie('do down down drown drown drown doing doing \
                                  done done done dead dead dead dead at and cat cat car car car')
        
        result = lab.autocomplete(trie, 'do', 2)
        expect = ['done','down']
        self.assertEqual(result,expect)
        
        result = lab.autocomplete(trie, 'd', 3)
        expect = ['dead', 'done', 'drown']
        self.assertEqual(result,expect)
        
        result = sorted(lab.autocomplete(trie, 'do', None))
        expect = sorted(['done', 'down', 'doing', 'do'])
        self.assertEqual(result,expect)

        
class Test_5_AutoCorrect(unittest.TestCase):
    def test_01_autocorrect(self):
        # Autocorrect on cat in small corpus
        trie = lab.make_word_trie("cats cattle hat car act at chat crate act car act")
        result = lab.autocorrect(trie, 'cat',4)
        self.assertIsInstance(result,list,"result not a list.")
        for w in result:
            self.assertIsInstance(w,str,"expecting list of strings.")
        result.sort()
        expect = ["act", "car", "cats", "cattle"]
        self.assertEqual(result,expect,msg="incorrect result from autocorrect.")

    def test_02_big_autocorrect(self):
        nums = {'thin': [0, 8, 10, None],
                'tom': [0, 2, 4, None],
                'mon': [0, 2, 15, 17, 20, None]}
        with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
            text = f.read()
        w = lab.make_word_trie(text)
        for i in sorted(nums):
            for n in nums[i]:
                result = lab.autocorrect(w, i, n)
                expected = read_expected('frank_autocorrect_%s_%s.pickle' % (i, n))
                self.assertEqual(len(result), len(expected), msg=('missing' if len(result) < len(expected)\
                    else 'too many') + ' autocorrect results for ' + repr(i) + ' with macount = ' + str(n))
                self.assertEqual(set(result), set(expected), msg='autocorrect included ' + repr(set(result) - set(expected))\
                    + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n))


class Test_6_Filter(unittest.TestCase):
    def test_01_filter(self):
        # Filter to select all words in trie
        trie = lab.make_word_trie("man mat mattress map me met a man a a a map man met")
        result = lab.word_filter(trie, '*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

        # All three-letter words in trie
        result = lab.word_filter(trie, '???')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("man", 3), ("map", 2), ("mat", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

        # Words beginning with 'mat'
        result = lab.word_filter(trie, 'mat*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mat", 1), ("mattress", 1)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

        # Words beginning with 'm', third letter is t
        result = lab.word_filter(trie, 'm?t*')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mat", 1), ("mattress", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

        # Words with at least 4 letters
        result = lab.word_filter(trie, '*????')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("mattress", 1)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

        # All words
        result = lab.word_filter(trie, '**')
        self.assertIsInstance(result,list,"result not a list.")
        result.sort()
        expect = [("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)]
        self.assertEqual(result,expect,msg="incorrect result from filter.")

    def test_02_big_filter(self):
        patterns = ('*ing', '*ing?', '****ing', '**ing**', '????', 'mon*',
                    '*?*?*?*', '*???')
        with open(os.path.join(TEST_DIRECTORY, 'resources', 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
            text = f.read()
        w = lab.make_word_trie(text)
        for ix, i in enumerate(patterns):
            result = lab.word_filter(w, i)
            expected = read_expected('frank_filter_%s.pickle' % (ix, ))
            self.assertEqual(len(result), len(expected), msg='incorrect word_filter of '+repr(i))
            self.assertEqual(set(result), set(expected), msg='incorrect word_filter of '+repr(i))


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)