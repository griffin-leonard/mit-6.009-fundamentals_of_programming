"""6.009 Lab 4 -- Tent Packing"""

# NO IMPORTS ALLOWED!


# Example bag_list entries:
#      vertical 3x1 bag: { (0,0), (1,0), (2,0) }
#      horizontal 1x3 bag: { (0,0), (0,1), (0,2) }
#      square bag: { (0,0), (0,1), (1,0), (1,1) }
#      L-shaped bag: { (0,0), (1,0), (1,1) }
#      C-shaped bag: { (0,0), (0,1), (1,0), (2,0), (2,1) }
#      reverse-C-shaped bag: { (0,0), (0,1), (1,1), (2,0), (2,1) }


def pack(tent_size, missing_squares, bag_list, max_vacancy):
    """
    Pack a tent with different sleeping bag shapes leaving up to max_vacancy squares open
    :param tent_size: (rows, cols) for tent grid
    :param missing_squares: set of (r, c) tuples giving location of rocks
    :param bag_list: list of sets, each describing a sleeping bag shape
    Each set contains (r, c) tuples enumerating contiguous grid
    squares occupied by the bag, coords are relative to the upper-
    left corner of the bag.  You can assume every bag occupies
    at least the grid (0,0).
    :param max_vacancy: maximum number of non-rock locations which can be unoccupied
    :return:  None if no packing can be found; otherwise a list giving the
    placement and type for each placed bag expressed as a dictionary
    with keys
        "anchor": (r, c) for upper-left corner of bag
        "shape": index of bag on bag list
    """
    #base case: if a valid combination is found
    if (tent_size[0]*tent_size[1])-len(missing_squares) <= max_vacancy:
        return []
    
    coord = findEmpty(tent_size, missing_squares)
    for b in range(len(bag_list)):
        bags = [] 
        occupied = missing_squares.copy()
        
        #add bag to tent if it fits
        if doesFit(occupied, coord, bag_list[b], tent_size):
            bags.append({'anchor':coord, 'shape':b})
            for square in bag_list[b]:
                occupied.add((coord[0]+square[0],coord[1]+square[1]))
            response = pack(tent_size, occupied, bag_list, max_vacancy) #recursively call pack
            if response != None:
                return response+bags
            
    if max_vacancy > 0:        
        occupied.add(coord)
        response = pack(tent_size, occupied, bag_list, max_vacancy-1) #recursively call pack   
        if response != None:
            return response   
    return None
            
def doesFit(occupied, anchor, bag, tent_size):
    """ Determine if a bag fits in the tent. 'bag' is the shape, 'anchor'
    is the coordinate of the top left corner of the bag. """
    for coord0 in bag:
        coord = (coord0[0]+anchor[0],coord0[1]+anchor[1])
        if coord in occupied:
            return False
        elif coord[0] < 0 or coord[0] >= tent_size[0]:
            return False
        elif coord[1] < 0 or coord[1] >= tent_size[1]:
            return False
    return True

def findEmpty(tent_size, missing_squares):#test the bag is placeing in valid coord 
    for row in range(tent_size[0]):
        for col in range(tent_size[1]):
            if (row,col) not in missing_squares:
                return (row,col)
    return None

        
bag_list = [
    {(0, 0), (1, 0), (2, 0)},  # vertical 3x1 bag
    {(0, 0), (0, 1), (0, 2)},  # horizontal 1x3 bag
    {(0, 0), (0, 1), (1, 0), (1, 1)},  # square bag
    {(0, 0), (1, 0), (1, 1)},  # L-shaped bag
    {(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)},  # C-shaped bag
    {(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)},  # reverse C-shaped bag
]


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
