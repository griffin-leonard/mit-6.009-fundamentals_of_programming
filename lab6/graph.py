"""This module contains the `Graph` interface used in Lab 6."""


class Graph:
    """Interface for a mutable graph that can answer queries."""

    def query(self, pattern):
        """Return a list of subgraphs matching `pattern`.

        Parameters:
            `pattern`: a list of tuples, where each tuple represents a node.
                The first element of the tuple is the label of the node, while
                the second element is a list of the neighbors of the node as
                indices into `pattern`. A single asterisk '*' in place of the
                label matches any label.

        Returns:
            a list of lists, where each sublist represents a match, its items
            being names corresponding to the nodes in `pattern`.

        """
        raise NotImplementedError("not implemented")

    def add_node(self, name, label=''):
        """Add a node with name `name` and label `label`."""
        raise NotImplementedError("not implemented")

    def remove_node(self, name):
        """Remove the node with name `name`."""
        raise NotImplementedError("not implemented")

    def add_edge(self, start, end):
        """Add a edge from `start` to `end`."""
        raise NotImplementedError("not implemented")

    def remove_edge(self, start, end):
        """Remove the edge from `start` to `end`."""
        raise NotImplementedError("not implemented")
