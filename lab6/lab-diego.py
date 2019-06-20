"""6.009 Lab 6 -- Gift Delivery."""


from graph import Graph

# NO ADDITIONAL IMPORTS ALLOWED!


class GraphFactory:
    """Factory methods for creating instances of `Graph`."""

    def __init__(self, graph_class):
        """Return a new factory that creates instances of `graph_class`."""
        self.graph_type = graph_class

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
        new_graph = self.graph_type()
        for i in range(len(adj_list)):
            try:
                new_graph.add_node(i, labels[i])
            except:
                new_graph.add_node(i)
        for i in range(len(adj_list)):   
            for neighbor in adj_list[i]:
                new_graph.add_edge(i, neighbor)
        return new_graph
                

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
        new_graph = self.graph_type()
        for node_name in adj_dict:
            try:
                new_graph.add_node(node_name, labels[node_name])
            except:
                new_graph.add_node(node_name)
        for node_name in adj_dict:
            for neighbor in adj_dict[node_name]:
                new_graph.add_edge(node_name, neighbor)
        return new_graph


class SimpleGraph(Graph):
    """Simple implementation of the Graph interface."""

    def __init__(self):
        self.adj_dict = {}
        self.labels = {}
        
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
        n = len(pattern)
        all_lst = self.query_all(n, pattern)
        true_lst = []
        for sublist in all_lst:
            if self.check_connectedness(sublist, pattern):
                true_lst.append(sublist)
        return true_lst
    
    def check_connectedness(self, sublist, pattern):
        for i in range(len(pattern)):
            tups = pattern[i]
            assoc_neighbs = tups[1]
            for neighb in assoc_neighbs:
                if not sublist[neighb] in self.adj_dict[sublist[i]]:
                    return False
        return True

    def query_all(self, n, pattern):
        pools = [tuple([key for key in self.adj_dict.keys()])]*n
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool if (self.valid_labels(x+[y], pattern) and y not in x)]
        return result
    
    def valid_labels(self, tentative_list, pattern):
        for i in range(len(tentative_list)):
            node_name = tentative_list[i]
            if self.labels[node_name] != pattern[i][0] and pattern[i][0] != "*":
                return False
        return True
                    
    def add_node(self, name, label=''):
        """Add a node with name `name` and label `label`."""
        if name in self.adj_dict:
            raise ValueError
        else:
            self.adj_dict[name] = []
            self.labels[name] = label
        

    def remove_node(self, name):
        """Remove the node with name `name`."""
        if name in self.adj_dict:
            del self.adj_dict[name]
            try:
                del self.labels[name]
            except:
                pass
        else:
            raise LookupError

    def add_edge(self, start, end):
        """Add a edge from `start` to `end`."""
        if start not in self.adj_dict or end not in self.adj_dict:
            raise LookupError
        if self.adj_dict[start] == None:
            self.adj_dict[start] = [end]
        else:
            if end in self.adj_dict[start]:
                raise ValueError
            self.adj_dict[start].append(end)       

    def remove_edge(self, start, end):
        """Remove the edge from `start` to `end`."""
        if start not in self.adj_dict or end not in self.adj_dict or end not in self.adj_dict[start]:
            raise LookupError
        self.adj_dict[start].remove(end)
        
    def change_label(self, node, new_label):
        self.labels[node] = new_label
    
    def get_label(self, node):
        return self.labels[node]

class CompactGraph(Graph):
    """Graph optimized for cases where many nodes have the same neighbors."""

    def __init__(self):
        self.neighborset_node_dict = {}
        self.node_list = []
        self.labels = {}
     
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
        n = len(pattern)
        all_lst = self.query_all(n, pattern)
        true_lst = []
        sorted_dict_as_list = sorted(self.neighborset_node_dict.items(), key = lambda x : len(x[1]), reverse = True)
        for sublist in all_lst:
            if self.check_connectedness(sublist, pattern, sorted_dict_as_list):
                true_lst.append(sublist)
        return true_lst
    
    def check_connectedness(self, sublist, pattern, sortedd):
        for i in range(len(pattern)):
            neighbors = pattern[i][1]         
            for neighbor in neighbors:
                end = sublist[neighbor]
                start = sublist[i]
                neighb_checks = False
                for (neighborset,nodeset) in sortedd:
                    if start in nodeset and end in neighborset:
                        neighb_checks = True
                        break
                if neighb_checks == False:
                    return False
        return True

    def query_all(self, n, pattern):
        pools = [tuple([key for key in self.node_list])]*n
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool if (self.valid_labels(x+[y], pattern) and y not in x)]
        return result
    
    def valid_labels(self, tentative_list, pattern):
        for i in range(len(tentative_list)):
            node_name = tentative_list[i]
            if self.labels[node_name] != pattern[i][0] and pattern[i][0] != "*":
                return False
        return True
                    
    def add_node(self, name, label=''):
        """Add a node with name `name` and label `label`."""
        if name in self.node_list:
            raise ValueError
        else:
            self.node_list.append(name)
            self.labels[name] = label
        

    def remove_node(self, name):
        """Remove the node with name `name`."""
        if name in self.node_list:
            self.node_list.remove(name)
            del self.labels[name]
        else:
            raise LookupError

    def add_edge(self, start, end):
        """Add a edge from `start` to `end`."""
        if start not in self.node_list or end not in self.node_list:
            raise LookupError
        start_already_exists = False
        start_current_neighborset = None
        for neighborset, nodelist in self.neighborset_node_dict.items():
            if start in nodelist:
                start_already_exists = True
                start_current_neighborset = neighborset
                break
        if start_already_exists == False: #if we havent even considered the node, then add it to the neighborset {end}
            self.neighborset_node_dict[frozenset({end})] = {start}
        else: #ok, so this guy already had a list of neighbors, but now we are updating it!
            h = set(start_current_neighborset)
            h.add(end)
            updated_neighborset = frozenset(h) #this is the new set of neighbors for our start
            if updated_neighborset in self.neighborset_node_dict: #if this neighborset already existed
                #lets remove start from the original nodeset
                self.neighborset_node_dict[start_current_neighborset].remove(start)
                #if this means the nodeset is equal to 0, lets remove the whole dicitonary entry
                if self.neighborset_node_dict[start_current_neighborset] == set():
                    del self.neighborset_node_dict[start_current_neighborset]
                #finally, lets add start to the nodeset of the relevant dicitonary entry
                self.neighborset_node_dict[updated_neighborset].add(start)
            else: #ok, now lets assume that this neighborset didnt exist
                #lets remove start from the original nodeset
                self.neighborset_node_dict[start_current_neighborset].remove(start)
                #if this means the nodeset is equal to 0, lets remove the whole dicitonary entry
                if self.neighborset_node_dict[start_current_neighborset] == set():
                    del self.neighborset_node_dict[start_current_neighborset]
                #finally, lets add create a new nodeset to accompany our relevant neighborset
                self.neighborset_node_dict[updated_neighborset] = set((start,))
                
    def remove_edge(self, start, end):
        """Remove the edge from `start` to `end`."""
        if start not in self.node_list or end not in self.node_list:
            raise LookupError
        for neighborset, nodeset in self.neighborset_node_dict.items():
            if start in nodeset:
                h = set(neighborset)
                h.remove(end)
                updated_neighborset = frozenset(h)
                nodeset.remove(start)
                break
        if updated_neighborset != set():
            try:
                self.neighborset_node_dict[updated_neighborset].add(start)
            except:
                self.neighborset_node_dict[updated_neighborset] = set(start)
        
        
    def change_label(self, node, new_label):
        self.labels[node] = new_label
    
    def get_label(self, node):
        return self.labels[node]

def allocate_teams(graph, k, stations, gift_labels):
    """Compute the number of teams needed to deliver each gift.

    It is guaranteed that there is exactly one node for each gift type and all
    building nodes have the label "building".

    Parameters:
        `graph`: an instance of a `Graph` implementation
        `k`: minimum number of buildings that a cluster needs to contain for a
             delivery to be sent there
        `stations`: mapping between each node name and a string representing
                    the name of the closest subway/train station
        `gift_labels`: a list of gift labels

    Returns:
        a dictionary mapping each gift label to the number of teams
        that Santa needs to send for the corresponding gift to be delivered

    """
    """
    here's what im going to do:
    -change the labels of the buildings to their corresponding station
    query the following pattern: [("gift", [1]),("*", [])] for all gifts
    this will give me a list of all the [gift, building pairs] that exist
    for each gift:
        go through the different station names associated with the gift
        if there are k or more buildings with the same station name, increase elf count by 1
    """
    for node_name, station_name in stations.items():
        graph.change_label(node_name, station_name)
    gift_bldg_pairs_dict = {} #dicitonary: keys are gifts, values is a list of buildings
    gift_elves_dict = {}
    for gift in gift_labels:
        gift_bldg_pairs_dict[gift] = []
        gift_elves_dict[gift] = 0
        for gift_bldg_pair in graph.query([(gift, [1]),("*", [])]):      
            gift_bldg_pairs_dict[gift].append(graph.get_label(gift_bldg_pair[1]))
    for gift, bldgs in gift_bldg_pairs_dict.items():
        for station in set(bldgs):
            if bldgs.count(station) >= k:
                gift_elves_dict[gift] += 1
    return gift_elves_dict

if __name__ == '__main__':
    # Put code here that you want to execute when lab.py is run from the
    # command line, e.g. small test cases.
    pass
