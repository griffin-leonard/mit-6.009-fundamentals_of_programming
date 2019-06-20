"""6.009 Lab 3 -- HyperMines"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


class MinesGame:
    def __init__(self, dimensions, bombs):
        """Start a new game.

        This method should properly initialize the "board", "mask",
        "dimensions", and "state" attributes.

        Args:
           dimensions (list): Dimensions of the board
           bombs (list): Bomb locations as a list of lists, each an
                         N-dimensional coordinate
        """
        # 2-Dimensions
        num_rows = dimensions[0]
        num_cols = dimensions[1]

        self.dimensions = [num_rows, num_cols]
        self.mask = self.make_board(dimensions, False)
        self.board = self.make_board(dimensions, 0)

        for bomb_row, bomb_col in bombs: # initialize bombs (will fail if dimensions > 2)
            self.board[bomb_row][bomb_col] = '.'

        for bomb in bombs:
            for neighbor in self.neighbors(bomb):
                row = neighbor[0]
                col = neighbor[1]
                if self.board[row][col] != '.':
                    self.board[row][col] += 1

        self.state = 'ongoing'
        
    def make_board(self, dimensions, elem):
        """Return a new game board

        This method currently initializes a 2-Dimensions board.
        (Optional) Update this method to return a board of N-Dimensions.

        Args:
            dimensions (list): Dimensions of the board
            elem (any): Initial value of every square on the board

        Returns:
            list: N-Dimensional board
        """
        # 2-Dimensions
        num_rows = dimensions[0]
        num_cols = dimensions[1]

        return [[elem for c in range(num_cols)] for r in range (num_rows)]

    def is_in_bounds(self, coords):
        """Returns whether the coordinates are within bound

        This method currently checks coordinate boundaries for a 2-Dimensions board.
        (Optional) Update this method to check boundaries for N-Dimensional boards.

        Args:
            coords (list): Coordinates of a square

        Returns:
            boolean: True if the coordinates are within bound and False otherwise
        """
        row = coords[0]
        col = coords[1]
        return 0 <= row < self.dimensions[0] and 0 <= col < self.dimensions[1]

    def neighbors(self, coords):
        """Return a list of the neighbors of a square

        This method currently returns the neighbors of a 2-Dimensions square.
        (Optional) Update this method to return the neighbors of an N-Dimensional square.

        Args:
            coords (list): List of coordinates for the square (integers)

        Returns:
            list: coordinates of neighbors
        """
        # 2-Dimensions
        row = coords[0]
        col = coords[1]

        all_neighbors = [] # Find all possible neighbors
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                all_neighbors.append([row + dx, col + dy])

        return [neighbor for neighbor in all_neighbors if self.is_in_bounds(neighbor)]
    
    def is_victory(self):
        """Returns whether there is a victory in the game.

        This method currently checks for victory in a 2-Dimensions board.
        A victory occurs when all non-bomb squares have been revealed.
        (Optional) Update this method to properly check for victory in an N-Dimensional board.

        Returns:
            boolean: True if there is a victory and False otherwise
        """
        # 2-Dimensions
        num_rows = self.dimensions[0]
        num_cols = self.dimensions[1]

        for row in range(num_rows):
            for col in range(num_cols):
                if self.board[row][col] == '.' and self.mask[row][col]: # A bomb square has been revealed
                    return False
                if self.board[row][col] != '.' and not self.mask[row][col]: # A non-bomb square is not yet revealed
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
        # 2-Dimensions
        row = coords[0]
        col = coords[1]

        if self.state != 'ongoing' or self.mask[row][col]:  # if defeated or already dug
            return 0

        if self.board[row][col] == '.': # if digging up a bomb
            self.mask[row][col] = True
            self.state = 'defeat'
            return 1

        count = 1
        self.mask[row][col] = True
        if self.board[row][col] == 0: # if digging up a regular square, recursively dig its neighbors
            for neighbor in self.neighbors(coords):
                count += self.dig(neighbor)

        self.state = 'victory' if self.is_victory() else 'ongoing'
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
        # 2-Dimensions
        num_rows = self.dimensions[0]
        num_cols = self.dimensions[1]
        board = self.make_board(self.dimensions, None) # New board to hold render result

        for row in range(num_rows): # Iterate through all the squares in the game and append their rendered form to board
            for col in range(num_cols):
                if xray or self.mask[row][col]: # Show value of a square if either xray is True or if square has been revealed
                    if self.board[row][col] == 0:
                        board[row][col] = ' '
                    else:
                        board[row][col] = str(self.board[row][col])
                else: # Otherwise hide the value using a '_' character
                    board[row][col] = '_'
        return board

    def dump(self):
        """Print a human-readable representation of this game.

        This method is for debugging and testing purposes only. DO NOT MODIFY THIS METHOD!
        """
        lines = ["dimensions: %s" % (self.dimensions, ),
                 "board: %s" % ("\n       ".join(map(str, self.board)), ),
                 "mask:  %s" % ("\n       ".join(map(str, self.mask)), ),
                 "state: %s" % (self.state, )]
        print("\n".join(lines))
