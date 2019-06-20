#!/usr/bin/env python3
import unittest
import lab
import json


class PatternFactory:
    @staticmethod
    def make_path_pattern(n, labels=None):
        labels = labels or ["*" for i in range(n)]
        return ([(labels[i], [i + 1]) for i in range(n)] +
                [(labels[n], [])])

    @staticmethod
    def make_cycle_pattern(n, labels=None):
        labels = labels or ["*" for i in range(n)]
        pattern = [(labels[i], [i+1]) for i in range(n - 1)]
        pattern.append((labels[n-1], [0]))
        return pattern

    @staticmethod
    def make_clique_pattern(n, labels=None):
        labels = labels or ["*" for i in range(n)]
        return [(labels[i], [j for j in range(n) if j != i])
                for i in range(n)]


class Test_1_QuerySmall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        factory = lab.GraphFactory(lab.FastGraph)
        adj = [[1, 3], [2], [0], []]
        labels = {0: "a", 1: "a", 2: "a", 3: "b"}
        cls.graph = factory.from_list(adj, labels=labels)

    def test_01(self):
        # All nodes.
        pattern = [('*', [])]
        expected = [[0], [1], [2], [3]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_02(self):
        # All edges.
        pattern = [('*', [1]), ('*', [])]
        expected = [[0, 1], [0, 3], [1, 2], [2, 0]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_03(self):
        # Paths of length 2.
        pattern = [('*', [1]), ('*', [2]), ('*', [])]
        expected = [[0, 1, 2], [1, 2, 0], [2, 0, 1], [2, 0, 3]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_04(self):
        # Paths of length 3.
        pattern = [('*', [1]), ('*', [2]), ('*', [3]), ('*', [])]
        expected = [[1, 2, 0, 3]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_05(self):
        # Paths of length 4.
        pattern = [('*', [1]), ('*', [2]), ('*', [3]), ('*', [4]), ('*', [])]
        expected = []
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_06(self):
        # Triangles.
        pattern = [('*', [1]), ('*', [2]), ('*', [0])]
        expected = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_07(self):
        # 2-legged stars.
        pattern = [('*', [1, 2]), ('*', []), ('*', [])]
        expected = [[0, 1, 3], [0, 3, 1]]
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_08(self):
        # 3-legged stars.
        pattern = [('*', [1, 2, 3]), ('*', []), ('*', []), ('*', [])]
        expected = []
        self.assertCountEqual(expected, self.graph.query(pattern))


class Test_2_QueryMedium(unittest.TestCase, PatternFactory):
    @classmethod
    def setUpClass(cls):
        with open('test_inputs/2.json', 'r') as f:
            graph_dict = json.load(f)
        adj_list = []
        labels = {}
        adj_dict = {}
        for i in range(len(graph_dict)):
            adj_list.append(graph_dict[str(i)][1])
            labels[i] = graph_dict[str(i)][0]
            adj_dict[i] = graph_dict[str(i)][1]

        factory = lab.GraphFactory(lab.FastGraph)
        cls.graph1 = factory.from_list(adj_list, labels=labels)
        cls.graph2 = factory.from_dict(adj_dict, labels=labels)

    def test_01(self):
        # Query exact labels.
        pattern = [('e', [])]
        expected = [[6], [7]]
        self.assertCountEqual(expected, self.graph1.query(pattern))

        pattern = ([('c', []), ('a', [0])])
        expected = [[2, 0], [3, 0], [15, 13]]
        self.assertCountEqual(expected, self.graph2.query(pattern))

        pattern = ([('#', [])])
        expected = []
        self.assertEqual(expected, self.graph1.query(pattern))

    def test_02(self):
        # Query cycles.
        with open('test_outputs/2.2.json', 'r') as f:
            expected = json.load(f)
        with open('test_inputs/2.2.json', 'r') as f:
            labels = json.load(f)

        for i in range(3, 7):
            with self.subTest(i=i):
                pattern = self.make_cycle_pattern(i, labels[str(i)])
                result1 = self.graph1.query(pattern)
                self.assertCountEqual(expected[str(i)], result1)
                result2 = self.graph2.query(pattern)
                self.assertCountEqual(expected[str(i)], result2)

    def test_03(self):
        # Query cliques.
        with open('test_outputs/2.3.json', 'r') as f:
            expected = json.load(f)
        with open("test_inputs/2.3.json", 'r') as f:
            labels = json.load(f)

        for i in range(3, 7):
            with self.subTest(i=i):
                pattern = self.make_clique_pattern(i, labels[str(i)])
                result1 = self.graph1.query(pattern)
                self.assertCountEqual(expected[str(i)], result1)
                result2 = self.graph2.query(pattern)
                self.assertCountEqual(expected[str(i)], result2)

    def test_04(self):
        # Query paths.
        with open('test_outputs/2.4.json', 'r') as f:
            expected = json.load(f)
        with open(f"test_inputs/2.4.json", 'r') as f:
            labels = json.load(f)

        for i in range(2, 9):
            with self.subTest(i=i):
                pattern = self.make_path_pattern(i, labels[str(i)])
                result1 = self.graph1.query(pattern)
                self.assertCountEqual(expected[str(i)], result1)
                result2 = self.graph2.query(pattern)
                self.assertCountEqual(expected[str(i)], result2)


class Test_3_QueryStars(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = lab.GraphFactory(lab.FastGraph)
        adj = ([[i+1] for i in range(0, 100000)] + [[i for i in range(1, 10)]])
        labels = {0: "b"}
        labels.update({1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h",
                       8: "i", 9: "j", 10: "k"})
        labels.update({i: "a" for i in range(11, 100001)})
        cls.graph = cls.factory.from_list(adj, labels)

    def test_01(self):
        # Smaller case, valid.
        pattern = [("a", [i for i in range(1, 10)]), ("b", []), ("c", []),
                   ("d", []), ("e", []), ("f", []), ("g", []), ("h", []),
                   ("i", []), ("j", [])]
        expected = [[100000, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        for i in range(10):
            with self.subTest(i=i):
                result = self.graph.query(pattern)
                self.assertCountEqual(expected, result)

    def test_02(self):
        # Smaller case, invalid.
        pattern = [("b", [i for i in range(1, 10)]), ("b", []), ("c", []),
                   ("d", []), ("e", []), ("f", []), ("g", []), ("h", []),
                   ("i", []), ("j", [])]
        expected = []
        for i in range(10):
            with self.subTest(i=i):
                result = self.graph.query(pattern)
                self.assertCountEqual(expected, result)

    def test_03(self):
        # Larger case.
        adj = [list(range(i, i + 10)) for i in range(100000)]
        adj += [[] for i in range(10)]
        centers = [42, 888, 1040]
        for n, i in enumerate(centers):
            n += 1
            adj[i] = list(range(i + 1, i + 100*n + 1))
        labels = {i:str(i) for i in range(100010)}

        graph = self.factory.from_list(adj, labels)

        for n, i in enumerate(centers):
            n += 1
            with self.subTest(i=n):
                self.maxDiff = None
                pattern = [(str(j), []) for j in range(i + 1, i + 100*n + 1)]
                pattern[50*n] = ('*', [j for j in range(100*n) if j != 50*n])
                expected = [[j for j in range(i + 1, i + 100*n + 1)]]
                expected[0][50*n] = i
                result = graph.query(pattern)
                self.assertCountEqual(expected, result)


class Test_4_QueryCliques(unittest.TestCase, PatternFactory):
    @classmethod
    def setUpClass(cls):
        max_size = 10
        factory = lab.GraphFactory(lab.FastGraph)
        adj = {(clique_size, member): [(clique_size, other)
                                       for other in range(clique_size)
                                       if other != member
                                       and not (member == clique_size - 1
                                                and other == clique_size - 2)]
               for clique_size in range(1, max_size + 1)
               for member in range(clique_size)}
        labels = {(clique_size, member): str(clique_size)
                  for clique_size in range(1, max_size + 1)
                  for member in range(clique_size)}
        cls.graph = factory.from_dict(adj, labels)

    def test_01(self):
        pattern = self.make_clique_pattern(10)
        expected = []
        self.assertCountEqual(expected, self.graph.query(pattern))

    def test_02(self):
        pattern = self.make_clique_pattern(9)
        # checking all of them would take too long
        n_expected = 725760
        expected_1 = [(10, 8), (10, 5), (10, 4), (10, 7), (10, 6), (10, 0),
                      (10, 3), (10, 1), (10, 2)]
        result = self.graph.query(pattern)
        self.assertEqual(n_expected, len(result))
        self.assertIn(expected_1, result)

    def test_03(self):
        labels = ["9" for _ in range(8)]
        pattern = self.make_clique_pattern(8, labels)
        # checking all of them would take too long
        n_expected = 80640
        expected_1 = [(9, 0), (9, 1), (9, 2), (9, 3), (9, 5), (9, 6), (9, 4),
                      (9, 7)]
        result = self.graph.query(pattern)
        self.assertEqual(n_expected, len(result))
        self.assertIn(expected_1, result)


class Test_5_Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = lab.GraphFactory(lab.FastGraph)

    @classmethod
    def _make_small_graph(cls):
        adj = [[1, 3], [2], [0], []]
        labels = {0: "a", 1: "a", 2: "a", 3: "b"}
        return cls.factory.from_list(adj, labels=labels)

    @classmethod
    def _make_star_graph(cls):
        adj = ([[100000] for i in range(0, 100000)] +
               [[i for i in range(1, 10)]])
        labels = {0: "b"}
        labels.update({1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h",
                       8: "i", 9: "j", 10: "k"})
        labels.update({i: "a" for i in range(11, 100001)})
        return cls.factory.from_list(adj, labels)

    @classmethod
    def _make_clique_graph(cls):
        adj_dict = {
            0: [1, 2, 3, 4, 5, 9],
            1: [0, 2, 3, 4, 5, 9],
            2: [0, 1, 3, 4, 5],
            3: [0, 1, 2, 4, 5],
            4: [0, 1, 2, 3, 5, 6, 7, 8],
            5: [0, 1, 2, 3, 4, 6, 7, 8, 10, 11],
            6: [4, 5, 7, 8, 10, 11],
            7: [4, 5, 6, 8],
            8: [4, 5, 6, 7],
            9: [0, 1],
            10: [5, 6, 11],
            11: [5, 6, 10]
        }
        for n in range(10000):
            for i in range(5):
                adj_dict[(i, n)] = [(j, n) for j in range(5)
                                    if i != j and not (i == 3 and j == 4)]
        return cls.factory.from_dict(adj_dict)

    def test_01(self):
        # Small graph.
        graph = self._make_small_graph()

        pattern = [("a", [1]), ("a", [2]), ("a", [0])]
        expected = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
        self.assertCountEqual(expected, graph.query(pattern))

        with self.assertRaises(ValueError):
            graph.add_node(1)

        with self.assertRaises(LookupError):
            graph.remove_node(5)
            graph.add_edge(3, 5)
            graph.remove_edge(2, 3)
            graph.remove_edge(2, 6)

        graph.remove_edge(2, 0)
        self.assertCountEqual([], graph.query(pattern))

        graph.add_node(5, label="b")
        graph.add_edge(0, 5)
        pattern = [("a", [1, 2]), ("a", []), ("b", [])]
        expected = [[0, 1, 3], [0, 1, 5]]
        self.assertCountEqual(expected, graph.query(pattern))

        graph.remove_node(1)
        pattern = [("*", [])]
        expected = [[2], [5], [0], [3]]
        self.assertCountEqual(expected, graph.query(pattern))

        pattern = [("a", [1, 2]), ("a", []), ("b", [])]
        expected = []
        self.assertCountEqual(expected, graph.query(pattern))

    def test_02(self):
        # Stars 1.
        graph = self._make_star_graph()
        graph.add_edge(100000, 0)

        pattern = ([("a", [i for i in range(1, 10)])] +
                   [("b", []), ("c", []), ("d", []), ("e", []), ("f", []),
                    ("g", []), ("h", []), ("i", []), ("j", [])])
        expected = [[100000, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    [100000, 0, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.assertCountEqual(expected, graph.query(pattern))

        graph.add_edge(2, 3)
        self.assertCountEqual(expected, graph.query(pattern))

        for i in range(10):
            graph.add_edge(99999, i)
        expected = [[100000, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    [100000, 0, 2, 3, 4, 5, 6, 7, 8, 9],
                    [99999, 0, 2, 3, 4, 5, 6, 7, 8, 9],
                    [99999, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.assertCountEqual(expected, graph.query(pattern))

    def test_03(self):
        # Stars 2.
        graph = self._make_star_graph()
        graph.remove_edge(2, 100000)

        pattern = ([("a", [i for i in range(1, 10)])] +
                   [("b", []), ("c", []), ("d", []), ("e", []), ("f", []),
                    ("g", []), ("h", []), ("i", []), ("j", [])])
        expected = [[100000, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.assertCountEqual(expected, graph.query(pattern))

        graph.remove_edge(100000, 1)
        expected = []
        for _ in range(10):
            self.assertCountEqual(expected, graph.query(pattern))

        pattern = ([("a", [i for i in range(1, 9)])] +
                   [("c", []), ("d", []), ("e", []), ("f", []), ("g", []),
                    ("h", []), ("i", []), ("j", [])])
        expected = [[100000, 2, 3, 4, 5, 6, 7, 8, 9]]
        for _ in range(10):
            self.assertCountEqual(expected, graph.query(pattern))

        graph.remove_node(2)
        graph.remove_node(3)
        graph.remove_node(4)
        pattern = ([("a", [i for i in range(1, 6)])] +
                   [("*", []), ("*", []), ("*", []), ("*", []), ("*", [])])
        with open("test_outputs/5.3.json", "r") as f:
            expected = json.load(f)
        self.assertCountEqual(expected, graph.query(pattern))

    def test_04(self):
        # Cliques 1.
        graph = self._make_clique_graph()
        with open("test_outputs/5.4.json", "r") as f:
            expected = json.load(f)

        pattern1 = [("*", [i for i in range(6) if i != j]) for j in range(6)]
        for i in range(1):
            self.assertCountEqual(expected['0'], graph.query(pattern1))

        pattern2 = [("*", [i for i in range(5) if i != j]) for j in range(5)]
        self.assertCountEqual(expected['1'], graph.query(pattern2))

        for i in range(4, 9):
            graph.add_edge(i, 9)
        for i in range(4, 9):
            graph.add_edge(9, i)
        self.assertCountEqual(expected['2'], graph.query(pattern1))

    def test_05(self):
        # Cliques 2.
        graph = self._make_clique_graph()
        graph.remove_edge(4, 5)

        with open("test_outputs/5.5.json", "r") as f:
            expected = json.load(f)

        pattern = [("*", [i for i in range(6) if i != j]) for j in range(6)]
        self.assertCountEqual(expected['0'], graph.query(pattern))

        pattern = [("*", [i for i in range(5) if i != j]) for j in range(5)]
        self.assertCountEqual(expected['1'], graph.query(pattern))

    def test_06(self):
        # Cliques 3.
        graph = self._make_clique_graph()
        graph.remove_node(5)

        with open("test_outputs/5.6.json", 'r') as f:
            expected = json.load(f)

        pattern = ([(j, [i for i in range(4) if i != j]) for j in range(3)] +
                   [(5, [i for i in range(4)])])
        self.assertCountEqual(expected['0'], graph.query(pattern))

        pattern = [(5, [1, 2, 3]), (6, [0, 2, 3]), (10, [0, 1, 3]),
                   (11, [0, 1, 2])]
        self.assertCountEqual(expected['1'], graph.query(pattern))

        pattern = [("*", [i for i in range(6) if i != j]) for j in range(6)]
        self.assertCountEqual(expected['2'], graph.query(pattern))


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
