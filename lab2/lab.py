# NO IMPORTS ALLOWED!

import json

def getActor(data, actorid):
    """ data is dicionary: {actor:actor id} """
    for actor in data.keys():
        if data[actor] == actorid:
            return actor
    raise Exception('actor id doesn\'t exist')
    
def did_x_and_y_act_together(data, actor_id_1, actor_id_2):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] """
    for mov in data:
        if actor_id_1 in mov and actor_id_2 in mov:
            return True
    return False

def baconDict(data):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] """
    neighbors = {}
    for mov in data:
        actor1,actor2 = mov[0],mov[1]
        if actor1 not in neighbors:
            neighbors[actor1] = set([actor2])
        else:
            neighbors[actor1].add(actor2)
        if actor2 not in neighbors:
            neighbors[actor2] = set([actor1])
        else:
            neighbors[actor2].add(actor1)
    for actor in neighbors:
        neighbors[actor] = list(neighbors[actor])
    return neighbors
    
def get_actors_with_bacon_number(data, n):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] """
    neighbors = baconDict(data)
    
    #if n=0 or n=1
    if n == 0:
        return set([4724])
    elif n == 1:
        return set(neighbors[4724])
    
    #for n>1
    queue = [(4724,0)]
    visited = set([])
    baconDicts = {0:visited}
    while queue:
        actor = queue.pop(0)
        if actor[0] not in visited:
            visited.add(actor[0])
            if actor[1] not in baconDicts:
                baconDicts[actor[1]] = set([actor[0]])
            else:
                baconDicts[actor[1]].add(actor[0])
            for ids in neighbors[actor[0]]:
                queue.append((ids,actor[1]+1))
    if n not in baconDicts:
        return set([])
    return baconDicts[n]

def get_bacon_path(data, actor_id):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] """
    neighbors = baconDict(data)
    queue = [[4724]]
    visited = set([])
    while queue:
        path = queue.pop(0)
        for ids in neighbors[path[-1]]:
            if ids == actor_id:
                path.append(ids)
                return path
            if ids not in visited:
                pcopy = path.copy()
                pcopy.append(ids)
                queue.append(pcopy)
            visited.add(ids)

def get_path(data, actor_id_1, actor_id_2):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] """
    neighbors = baconDict(data)
    queue = [[actor_id_1]]
    visited = set([])
    while queue:
        path = queue.pop(0)
        for ids in neighbors[path[-1]]:
            if ids == actor_id_2:
                path.append(ids)
                return path
            if ids not in visited:
                pcopy = path.copy()
                pcopy.append(ids)
                queue.append(pcopy)
            visited.add(ids)

def getMovie(data, actor1, actor2):
    """ data is list: [[actor_id_1, actor_id_2, film_id]] 
        actor1 and actor2 are id numbers """
    for mov in data:
        if actor1 in mov and actor2 in mov:
            return mov[2]
    raise Exception('actors did\'t act together')

if __name__ == '__main__':
    with open('resources/small.json') as f:
        smalldb = json.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    #for 2.2
#    names = json.load(open('resources/names.json','r'))
#    print(test['Ramya Pratt'])
#    print(getActor(names,587452))
    
    #for 3
#    names = json.load(open('resources/names.json','r'))
#    small = json.load(open('resources/small.json','r'))
#    id1,id2 = names['Jennifer Pisana'],names['Yvonne Zima']
#    print(did_x_and_y_act_together(small,id1,id2))
#    id1,id2 = names['Natascha McElhone'],names['Joseph McKenna']
#    print(did_x_and_y_act_together(small,id1,id2))
    
    #for 4
#    tiny = json.load(open('resources/tiny.json','r'))
#    neighbors = baconDict(tiny)
#    print(neighbors[4724])  
#    print(get_actors_with_bacon_number(tiny, 2))
#    print(get_actors_with_bacon_number(tiny, 3))
#    large = json.load(open('resources/large.json','r'))
#    ids = get_actors_with_bacon_number(large, 6)
#    names = json.load(open('resources/names.json','r'))
#    actors = set([])
#    for actor in ids:
#        actors.add(getActor(names,actor))
#    print(actors)

    #for 5
#    tiny = json.load(open('resources/tiny.json','r'))
#    print(get_bacon_path(tiny, 1640))
#    names = json.load(open('resources/names.json','r'))
#    name = names['Jonny Cruz']
#    large = json.load(open('resources/large.json','r'))
#    ids = get_bacon_path(large, name)
#    id1,id2 = names['Antonia Torrens'],names['Robert De Niro']
#    ids = get_path(large,id1,id2)
#    actors = []
#    for actor in ids:
#        actors.append(getActor(names,actor))
#    print(actors)
    
    #for 6
#    large = json.load(open('resources/large.json','r'))
#    names = json.load(open('resources/names.json','r'))
#    id1,id2 = names['Andie MacDowell'],names['Iva Ilakovac']
#    path = get_path(large,id1,id2)
#    movielist = []
#    for i in range(len(path)-1):
#        movielist.append(getMovie(large,path[i],path[i+1]))
#    movies = json.load(open('resources/movies.json','r'))
#    movienames = []
#    for mov in movielist:
#        for key in movies:
#            if movies[key] == mov:
#                movienames.append(key)
#    print(movienames)
