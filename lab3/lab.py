"""6.009 Lab 3 -- HyperMines"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def setValue(board, coords, value):
    if len(coords) == 1:
        board[coords[0]] = value
    else:
        setValue(board[coords[0]],coords[1:],value)

def getValue(board, coords):
    if len(coords) == 1:
        return board[coords[0]]
    return getValue(board[coords[0]],coords[1:])

def possibleCoordinates(dimensions):
    coordList = []
    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            coord = [i]
            coordList.append(coord)
        return coordList
    
    for i in range(dimensions[0]):
        for coord0 in possibleCoordinates(dimensions[1:]):
            coord = [i]+coord0
            coordList.append(coord)
    return coordList


class HyperMinesGame:
    def __init__(self, dimensions, bombs):
        """Start a new game.

        This method should properly initialize the "board", "mask",
        "dimensions", and "state" attributes.

        Args:
           dimensions (list): Dimensions of the board
           bombs (list): Bomb locations as a list of lists, each an
                         N-dimensional coordinate
        """
        self.dimensions = dimensions
        self.state = 'ongoing' 
        self.mask = self.make_board(dimensions,False)
        self.board = self.make_board(dimensions,0)
        self.allCoords = possibleCoordinates(self.dimensions)
        for b in bombs:
            self.set_coords(b,'.')
            for neighbor in self.neighbors(b):
                value = self.get_coords(neighbor)
                if value != '.':
                    self.set_coords(neighbor,value+1)

    def get_coords(self, coords):
        """Get the value of a square at the given coordinates on the board.

        (Optional) Implement this method to return the value of a square at the given
        coordinates.

        Args:
            coords (list): Coordinates of the square

        Returns:
            any: Value of the square
        """
        return getValue(self.board,coords)

    def set_coords(self, coords, value):
        """Set the value of a square at the given coordinates on the board.

        (Optional) Implement this method to set the value of a square at the given
        coordinates.

        Args:
            coords (list): Coordinates of the square
        """
        setValue(self.board,coords,value)

    def make_board(self, dimensions, elem):
        """Return a new game board

        (Optional) Implement this method to return a board of N-Dimensions.

        Args:
            dimensions (list): Dimensions of the board
            elem (any): Initial value of every square on the board

        Returns:
            list: N-Dimensional board
        """
        if len(dimensions) == 1:
            return [elem for x in range(dimensions[0])]
        return [self.make_board(dimensions[1:],elem) for x in range(dimensions[0])]
        
    def is_in_bounds(self, coords):
        """Return whether the coordinates are within bound

        (Optional) Implement this method to check boundaries for N-Dimensional boards.

        Args:
            coords (list): Coordinates of a square

        Returns:
            boolean: True if the coordinates are within bound and False otherwise
        """
        for c,d in zip(coords,self.dimensions):
            if c < 0 or c >= d:
                return False
        return True

    def neighbors(self, coords):
        """Return a list of the neighbors of a square

        (Optional) Implement this method to return the neighbors of an N-Dimensional square.

        Args:
            coords (list): List of coordinates for the square (integers)

        Returns:
            list: coordinates of neighbors
        """
        neighborList = []
        self.consNeighbors(coords,0,neighborList)
        return neighborList
    
    def consNeighbors(self,coords,index,neighbors):
        if index == len(coords)-1:
            for dx in (-1,0,1):
                coord = coords.copy()
                coord[index] += dx
                if self.is_in_bounds(coord):
                    neighbors.append(coord)
    
        else:
            for dx in (-1,0,1):
                coord = coords.copy()
                coord[index] += dx
                self.consNeighbors(coord, index+1, neighbors)
   
        return neighbors
        
    def is_victory(self):
        """Returns whether there is a victory in the game.

        A victory occurs when all non-bomb squares have been revealed.
        (Optional) Implement this method to properly check for victory in an N-Dimensional board.

        Returns:
            boolean: True if there is a victory and False otherwise
        """
        for coord in self.allCoords:
            board = getValue(self.board,coord)
            isDug = getValue(self.mask,coord)
            if board == '.' and isDug:
                return False
            if board != '.' and not isDug:
                return False
        return True

    def dig(self, coords):
        """Recursively dig up square at coords and neighboring squares.

        Update the mask to reveal square at coords; then recursively reveal its
        neighbors, as long as coords does not contain and is not adjacent to a
        bomb.  Return a number indicating how many squares were revealed.  No
        action should be taken and 0 returned if the incoming state of the game
        is not "ongoing".

        The updated state is "defeat" when at least one bomb is visible on the
        board after digging, "victory" when all safe squares (squares that do
        not contain a bomb) and no bombs are visible, and "ongoing" otherwise.

        Args:
           coords (list): Where to start digging

        Returns:
           int: number of squares revealed
        """
        #if defeated or already dug
        if self.state != 'ongoing' or getValue(self.mask,coords):
            return 0
        
        #if digging up a bomb
        if getValue(self.board,coords) == '.':
            setValue(self.mask,coords,True)
            self.state = 'defeat'
            return 1
            
        count = 1
        setValue(self.mask,coords,True)
        #if digging up a regular square, recursively dig its neighbors
        if getValue(self.board,coords) == 0:
            for neighbor in self.neighbors(coords):
                count += self.dig(neighbor)
           
        if self.is_victory():
            self.state = 'victory'
        return count
                
    def render(self, xray=False):
        """Prepare the game for display.

        Returns an N-dimensional array (nested lists) of "_" (hidden squares),
        "." (bombs), " " (empty squares), or "1", "2", etc. (squares
        neighboring bombs).  The mask indicates which squares should be
        visible.  If xray is True (the default is False), the mask is ignored
        and all cells are shown.

        Args:
           xray (bool): Whether to reveal all tiles or just the ones allowed by
                        the mask

        Returns:
           An n-dimensional array (nested lists)
        """
        rendering = self.make_board(self.dimensions, None)
        for coord in self.allCoords:
            if xray or getValue(self.mask,coord):
                if getValue(self.board,coord) == 0:
                    setValue(rendering,coord,' ')
                else:
                    value = str(getValue(self.board,coord))
                    setValue(rendering,coord,value)
            else:
                setValue(rendering,coord,'_')
        return rendering

    # ***Methods below this point are for testing and debugging purposes only. 
    #    Do not modify anything here!***

    def dump(self):
        """Print a human-readable representation of this game."""
        lines = ["dimensions: %s" % (self.dimensions, ),
                 "board: %s" % ("\n       ".join(map(str, self.board)), ),
                 "mask:  %s" % ("\n       ".join(map(str, self.mask)), ),
                 "state: %s" % (self.state, )]
        print("\n".join(lines))

    @classmethod
    def from_dict(cls, d):
        """Create a new instance of the class with attributes initialized to
        match those in the given dictionary."""
        game = cls.__new__(cls)
        for i in ('dimensions', 'board', 'state', 'mask'):
            setattr(game, i, d[i])
        return game
    