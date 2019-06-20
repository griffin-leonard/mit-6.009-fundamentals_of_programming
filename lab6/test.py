#!/usr/bin/env python3
import os
import unittest
import lab
import json


class CustomTest:
    class TestQuerySmall(unittest.TestCase):
        def setUp(self):
            self.adj_list = [[1, 3], [2], [0], []]

        def test_01(self):
            # Add new node and edges.
            self.graph.add_node(5)
            try:
                self.graph.add_edge(2, 5)
            except LookupError:
                self.fail("could not add edge between nodes 2 and 5")

            try:
                self.graph.remove_node(5)
            except LookupError:
                self.fail("node 5 does not exists")

            with self.assertRaises(LookupError) as context:
                self.graph.add_edge(2, 5)

        def test_02(self):
            # Try to add existing node, edges between nonexistent nodes.
            with self.assertRaises(ValueError) as context:
                self.graph.add_node(1)

            with self.assertRaises(LookupError) as context:
                self.graph.remove_node(5)
                self.graph.add_edge(3, 5)
                self.graph.remove_edge(2, 3)
                self.graph.remove_edge(2, 6)

        def test_03(self):
            # Query all nodes.
            pattern = [('*', [])]
            expected = [[0], [1], [2], [3]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_04(self):
            # Query all edges.
            pattern = [('*', [1]), ('*', [])]
            expected = [[0, 1], [0, 3], [1, 2], [2, 0]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_05(self):
            # Query paths of length 2.
            pattern = [('*', [1]), ('*', [2]), ('*', [])]
            expected = [[0, 1, 2], [1, 2, 0], [2, 0, 1], [2, 0, 3]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_06(self):
            # Query paths of length 3.
            pattern = [('*', [1]), ('*', [2]), ('*', [3]), ('*', [])]
            expected = [[1, 2, 0, 3]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_07(self):
            # Query paths of length 4.
            pattern = [('*', [1]), ('*', [2]), ('*', [3]), ('*', [4]), ('*', [])]
            expected = []
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_08(self):
            # Query triangles.
            pattern = [('*', [1]), ('*', [2]), ('*', [0])]
            expected = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_09(self):
            # Query 2-legged stars.
            pattern = [('*', [1, 2]), ('*', []), ('*', [])]
            expected = [[0, 1, 3], [0, 3, 1]]
            self.assertCountEqual(expected, self.graph.query(pattern))

        def test_10(self):
            # Query 3-legged stars.
            pattern = [('*', [1, 2, 3]), ('*', []), ('*', []), ('*', [])]
            expected = []
            self.assertCountEqual(expected, self.graph.query(pattern))

    class TestQueryMedium(unittest.TestCase):
        def setUp(self):
            with open('resources/graph1.json', 'r') as f:
                graph_dict = json.load(f)
            self.adj_list = []
            self.labels = {}
            self.adj_dict = {}
            for i in range(len(graph_dict)):
                self.adj_list.append(graph_dict[str(i)][1])
                self.labels[i] = graph_dict[str(i)][0]
                self.adj_dict[i] = graph_dict[str(i)][1]

        def test_01(self):
            # Query exact labels.
            result1 = self.graph1.query([('e', [])])
            expected1 = [[6], [7]]
            self.assertCountEqual(expected1, result1)

            result2 = self.graph2.query([('c', []), ('a', [0])])
            expected2 = [[2, 0], [3, 0], [15, 13]]
            self.assertCountEqual(expected2, result2)

            result3 = self.graph1.query([('#', [])])
            self.assertEqual(result3, [])

        def test_02(self):
            # Query cycles.
            def make_cycle_pattern(n, labels=None):
                labels = labels or ["*" for i in range(n)]
                pattern = [(labels[i], [i+1]) for i in range(n - 1)]
                pattern.append((labels[n-1], [0]))
                return pattern

            with open('resources/expected_cycles.json', 'r') as f:
                expected = json.load(f)
            with open('resources/labels_cycles.json', 'r') as f:
                labels = json.load(f)
            for i, n in enumerate((3, 4, 5, 6)):
                graph = self.graph1
                if i % 2 == 1:
                    graph = self.graph2
                pattern = make_cycle_pattern(n, labels[str(n)])
                self.assertCountEqual(expected[str(n)], graph.query(pattern))

        def test_03(self):
            # Query cliques.
            def make_clique_pattern(n, labels=None):
                labels = labels or ["*" for i in range(n)]
                return [(labels[i], [j for j in range(n) if j != i])
                        for i in range(n)]

            with open('resources/expected_cliques.json', 'r') as f:
                expected = json.load(f)
            with open(f"resources/labels_cliques.json", 'r') as f:
                labels = json.load(f)
            for i, n in enumerate((3, 4, 5, 6)):
                graph = self.graph1
                if i % 2 == 1:
                    graph = self.graph2
                pattern = make_clique_pattern(n, labels[str(n)])
                results = graph.query(pattern)
                self.assertCountEqual(expected[str(n)], results)

        def test_04(self):
            # Query paths.
            def make_path_pattern(n, labels=None):
                labels = labels or ["*" for i in range(n)]
                return [(labels[i], [i+1]) for i in range(n)] + [(labels[n], [])]

            with open('resources/expected_paths.json', 'r') as f:
                expected = json.load(f)
            with open(f"resources/labels_paths.json", 'r') as f:
                labels = json.load(f)
            for i, n in enumerate((2, 3, 4, 5, 6, 7, 8)):
                graph = self.graph1
                if i % 2 == 1:
                    graph = self.graph2
                pattern = make_path_pattern(n, labels[str(n)])
                results = graph.query(pattern)
                self.assertCountEqual(expected[str(n)], results)


class Test_1_SimpleGraphSmall(CustomTest.TestQuerySmall):
    def setUp(self):
        super().setUp()
        factory = lab.GraphFactory(lab.SimpleGraph)
        self.graph = factory.from_list(self.adj_list)


class Test_2_CompactGraphSmall(CustomTest.TestQuerySmall):
    def setUp(self):
        super().setUp()
        factory = lab.GraphFactory(lab.CompactGraph)
        self.graph = factory.from_list(self.adj_list)


class Test_3_SimpleGraphMedium(CustomTest.TestQueryMedium):
    def setUp(self):
        super().setUp()
        factory = lab.GraphFactory(lab.SimpleGraph)
        self.graph1 = factory.from_list(self.adj_list, labels=self.labels)
        self.graph2 = factory.from_dict(self.adj_dict, labels=self.labels)


class Test_4_CompactGraphMedium(CustomTest.TestQueryMedium):
    def setUp(self):
        super().setUp()
        factory = lab.GraphFactory(lab.CompactGraph)
        self.graph1 = factory.from_list(self.adj_list, labels=self.labels)
        self.graph2 = factory.from_dict(self.adj_dict, labels=self.labels)


class Test_5_AllocationSmall(unittest.TestCase):
    def test_01(self):
        adj_list = [[5], [6], [5], [5], [5], [0, 2, 3, 4], [1]]
        labels = {i: "building" for i in range(5)}
        labels.update({5: "toy", 6: "candy"})
        labels = {0: "building", 1: "building", 2: "building", 3: "building",
                  4: "building", 5: "toy", 6: "candy"}
        factory = lab.GraphFactory(lab.SimpleGraph)
        graph = factory.from_list(adj_list, labels=labels)
        stations = {0: "South", 1: "South", 2: "North", 3: "South", 4: "South"}
        result = lab.allocate_teams(graph, 3, stations, ["toy", "candy"])
        self.assertEqual({"toy": 1, "candy": 0}, result)


class Test_6_AllocationMedium(unittest.TestCase):
    def _test_result(self, k):
        adj_list = [[11], [11], [11], [11], [11], [10], [10, 11],
                    [11], [10], [10], [5, 6, 8, 9],
                    [0, 1, 2, 3, 4, 6, 7]]
        labels = {i: "building" for i in range(10)}
        labels.update({10: "puppy", 11: "candy"})
        factory = lab.GraphFactory(lab.SimpleGraph)
        graph = factory.from_list(adj_list, labels=labels)
        stations = {0: "Old Square", 1: "Old Square", 2: "Old Square",
                    3: "Old Square", 4: "Town Hall", 5: "Town Hall",
                    6: "Town Hall", 7: "South Station", 8: "Ice Rink",
                    9: "Ice Rink"}
        gifts = ["puppy", "candy"]
        return lab.allocate_teams(graph, k, stations, gifts)

    def test_01(self):
        self.assertEqual({"puppy": 0, "candy": 0}, self._test_result(5))

    def test_02(self):
        self.assertEqual({"puppy": 0, "candy": 1}, self._test_result(4))

    def test_03(self):
        self.assertEqual({"puppy": 0, "candy": 1}, self._test_result(3))

    def test_04(self):
        self.assertEqual({"puppy": 2, "candy": 2}, self._test_result(2))

    def test_05(self):
        self.assertEqual({"puppy": 2, "candy": 3}, self._test_result(1))


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
