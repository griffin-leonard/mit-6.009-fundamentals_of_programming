"""6.009 Lab 7 -- Faster Gift Delivery."""


from graph import Graph

# NO ADDITIONAL IMPORTS ALLOWED!

permutations = []
permutations2 = set([])

def getPerms(l, path=[]):
    """ Get all permutations from a list of a list. Used as a helper 
    function for query. """
    global permutations
    if not l:
        permutations.append(path)
        return
    for item in l[0]:
        if item not in path:
            getPerms(l[1:], path+[item])

class GraphFactory:
    """Factory methods for creating instances of `Graph`."""

    def __init__(self, graph_class):
        """Return a new factory that creates instances of `graph_class`."""
        self.graphClass = graph_class

    def from_list(self, adj_list, labels=None):
        """Create and return a new graph instance.

        Use a simple adjacency list as source, where the `labels` dictionary
        maps each node name to its label.

        Parameters:
            `adj_list`: adjacency list representation of a graph
                        (as a list of lists)
            `labels`: dictionary mapping each node name to its label;
                      by default it's None, which means no label should be set
                      for any of the nodes

        Returns:
            new instance of class implementing `Graph`

        """
        graph = self.graphClass()
        #add the nodes
        for i in range(len(adj_list)):
            if labels == None:
                graph.add_node(i)
            else:
                graph.add_node(i, labels[i])
                
        #add the edges
        for i, node in enumerate(adj_list):
            for adj in node:
                graph.add_edge(i, adj)
        return graph

    def from_dict(self, adj_dict, labels=None):
        """Create and return a new graph instance.

        Use a simple adjacency dictionary as source where the `labels`
        dictionary maps each node name its label.

        Parameters:
            `adj_dict`: adjacency dictionary representation of a graph
            `labels`: dictionary mapping each node name to its label;
                      by default it's None, which means no label should be set
                      for any of the nodes

        Returns:
            new instance of class implementing `Graph`

        """
        graph = self.graphClass()
        #add the nodes
        for node in adj_dict:
            if labels is None:
                graph.add_node(node)
            else:
                graph.add_node(node, labels[node])
        
        #add the edges
        for node, l in adj_dict.items():
            for adj in l:
                graph.add_edge(node, adj)
        return graph

class FastGraph(Graph):
    """Faster implementation of `Graph`.

    Has extra optimizations for star and clique patterns.
    """

    def __init__(self):
        self.graph = {} #node -> list of adjacent nodes
        self.labels = {} #label -> list of nodes 
        self.nodes = {} #node -> label
        self.cliques = {} #nodes -> set of cliques (clique = frozenset of nodes)
    
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
        #check for star and clique patterns
        index = None
        clique = True
        for i,tup in enumerate(pattern):
            if len(tup[1]) != len(pattern)-1:
                clique = False
            else:
                index = i
                for j,tupl in enumerate(pattern):
                    if j != index and tupl[1] != []:
                        index = None
                if not clique:
                    break
        if clique:
            return self.query_clique(pattern)
        
        #get a list of lists, where each sublist contains all the nodes 
        #matching the label given by pattern at the sublist's index
        nodesByLabel = []
        for tup in pattern:
            label = tup[0]
            if label == '*': 
                allNodes = list(self.graph.keys())
                nodesByLabel.append(allNodes)
            elif label not in self.labels:
                nodesByLabel.append([])
            else:
                nodesByLabel.append(self.labels[label])
        
        if index is not None:
            return self.query_star(pattern, nodesByLabel, index)           
            
        #process a queue of incomplete solutions and add a solution to result if it is complete
        result = []
        queue = [[None]*len(pattern)]
        while queue:
            subresult = queue.pop(0)
            
            #confirm that completed solution is valid
            if None not in subresult and subresult not in result:
                valid = True
                for n in range(len(pattern)):
                    for i in pattern[n][1]:
                        if subresult[i] not in self.graph[subresult[n]]:
                            valid = False
                if valid:
                    result.append(subresult)
            
            #use query_helper to fill in the next empty index
            else:
                for i,elem in enumerate(subresult):
                    if elem is None:
                        queue.extend(self.query_helper(pattern, nodesByLabel, subresult, i))
                        break
        return result
    
    def query_star(self, pattern, nodesByLabel, i):
        """ Helper function for query for star patterns. """
        #create a list of center nodes for the star pattern
        centers = []
        for node in nodesByLabel[i]:
            if len(self.graph[node]) >= len(pattern)-1:
                centers.append(node)
        del nodesByLabel[i]
        
        result = []
        global permutations
        for node in centers:
            permutations = []
            
            #get a nodesByLabel-like list that only contains nodes adjacent to center node
            pat = []
            for l in nodesByLabel:
                patinner = []
                for pos in l:
                    if pos in self.graph[node]:
                        patinner.append(pos)
                pat.append(patinner)
            
            #construct results from permutations
            getPerms(pat)
            for perm in permutations:
                if i <= len(perm):
                    result.append(perm[:i]+[node]+perm[i:])
                else:
                    perm.append(node)
                    result.append(perm)
        return result
    
    def query_clique(self, pattern):
        """ Helper function for query for clique patterns. """
        #make a set of cliques with adequate size
        bigcliques = set([])
        for node in self.cliques:
            for clique in self.cliques[node]:
                if len(clique) >= len(pattern):
                    bigcliques.add(clique)
        
        #get permutations of those cliques and check labels as you go
        global permutations2
        permutations2 = set([])        
        for clique in bigcliques:
            l = [list(clique)]*len(pattern)
            self.getPerms2(l, pattern)
        result = []
        for perm in permutations2:
            result.append(list(perm))
        return result
                    
    def query_helper(self, pattern, nodesByLabel, subresult, i):
        """ Helper function for query. """
        result = []
        for node in nodesByLabel[i]:
            if node not in subresult:
                
                #check to see if node can be validly inserted
                valid = True
                for j,tup in enumerate(pattern):
                    for k in tup[1]:
                        if subresult[j] is not None:
                            if j == i and subresult[j] not in self.graph[node]:
                                valid = False
                            elif k == i and node not in self.graph[subresult[j]]:
                                valid = False
                                
                if valid:    
                    sub = subresult.copy()
                    sub[i] = node
                    #add to result if answer cannot be added to
                    if len(pattern[i][1]) == 0 or None not in sub:
                        result.append(sub)
                    #otherwise recursively call query_helper to fill in the next empty index
                    else:
                        for j in pattern[i][1]:
                            resultlist = []
                            if sub[j] is None:
                                resultlist = self.query_helper(pattern, nodesByLabel, sub, j)
                            result.extend(resultlist)
        return result

    def getPerms2(self, l, pattern, path=[]):
        """ Get all permutations from a list of a list and checks that they match pattern. 
        Used as a helper function for query. """
        global permutations2
        if not l:
            permutations2.add(tuple(path))
            return
        for item in l[0]:
            if item not in path and (pattern[0][0] == self.nodes[item] or pattern[0][0] == '*'):
                self.getPerms2(l[1:], pattern[1:], path+[item])
               
    def add_node(self, name, label=''):
        """Add a node with name `name` and label `label`."""
        if name in self.graph:
            raise ValueError
        else:
            self.graph[name] = []
            self.nodes[name] = label
            self.cliques[name] = set([frozenset([name])])
            if label not in self.labels:
                self.labels[label] = [name]
            else:
                self.labels[label].append(name)

    def remove_node(self, name):
        """Remove the node with name `name`."""
        if name not in self.graph:
            raise LookupError
        else:
            del self.graph[name]
            label = self.nodes[name]
            self.labels[label].remove(name)
            del self.nodes[name]
            del self.cliques[name]
            for node in self.cliques:
                for clique in self.cliques[node].copy():
                    if name in clique:
                        newset = set(clique)
                        newset.remove(name)
                        newset = frozenset(newset)
                        self.cliques[node].add(newset)
                        self.cliques[node].remove(clique)
                        
    def add_edge(self, start, end):
        """Add a edge from `start` to `end`."""
        if start not in self.graph or end not in self.graph:
            raise LookupError
        elif end in self.graph[start]:
            raise ValueError
        else:
            self.graph[start].append(end)
            if start in self.graph[end]:
                newset = frozenset([start,end])
                self.cliques[start].add(newset)
                self.cliques[end].add(newset)
                for clique in self.cliques[start].copy():
                    valid = True
                    for node in clique:
                        if node not in self.graph[end] or end not in self.graph[node]:
                            valid = False
                    if valid:
                        newset = set(clique)
                        newset.add(end)
                        newset = frozenset(newset)
                        for n in newset:
                            self.cliques[n].add(newset)

    def remove_edge(self, start, end):
        """Remove the edge from `start` to `end`."""
        if start not in self.graph or end not in self.graph or end not in self.graph[start]:
            raise LookupError
        else:
            self.graph[start].remove(end)
            for node in self.cliques:
                for clique in self.cliques[node].copy():
                    if start in clique and end in clique:
                        newset = set(clique)
                        newset.remove(start)
                        newset = frozenset(newset)
                        self.cliques[node].add(newset)
                        self.cliques[node].remove(clique)

if __name__ == '__main__':
    pass
