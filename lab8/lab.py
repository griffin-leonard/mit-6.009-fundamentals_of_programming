"""6.009 Spring 2019 Lab 8 -- 6.009 Zoo"""

# NO IMPORTS ALLOWED!

class Constants:
    """
    A collection of game-specific constants.

    You can experiment with tweaking these constants, but
    remember to revert the changes when running the test suite!
    """
    # width and height of keepers
    KEEPER_WIDTH = 31
    KEEPER_HEIGHT = 31

    # width and height of animals
    ANIMAL_WIDTH = 31
    ANIMAL_HEIGHT = 31

    # width and height of food
    FOOD_WIDTH = 11
    FOOD_HEIGHT = 11

    # width and height of rocks
    ROCK_WIDTH = 51
    ROCK_HEIGHT = 51

    # thickness of the path
    PATH_THICKNESS = 31

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'OverreachingZookeeper': '1f477',
        'food': '1f34e'
    }

    KEEPER_INFO = {'SpeedyZookeeper':
                   {'price': 250,
                    'range': 50,
                    'throw_speed_mag': 20},
                   'ThriftyZookeeper':
                   {'price': 100,
                    'range': 100,
                    'throw_speed_mag': 15},
                   'OverreachingZookeeper':
                   {'price': 150,
                    'range': 150,
                    'throw_speed_mag': 5}
                   }


class NotEnoughMoneyError(Exception):
    """A custom exception to be used when insufficient funds are available
    to hire new zookeepers."""
    pass



################################################################################
################################################################################
# Static methods.

def distance(a, b):
    """Returns the Euclidian distance between the two tuple coordinates."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def get_path(corners):
    """Returns a list of coordinates on the path."""
    full_path = []
    for i in range(len(corners)-1):
        #if the path segment is a horizontal line
        if corners[i][1] == corners[i+1][1]:
            #animal is moving right
            if corners[i][0] < corners[i+1][0]:
                Xvals = range(int(corners[i][0]+1), int(corners[i+1][0]+1))
                for val in Xvals:
                    coord = (val, corners[i][1])
                    full_path.append(coord)
            #animal is moving left
            else:
                Xvals = range(int(corners[i+1][0]), int(corners[i][0]))
                subPath = []
                for val in Xvals:
                    coord = (val, corners[i][1])
                    subPath = [coord] + subPath
                full_path.extend(subPath)
        #if the path segment is a vertical line
        else:
            #animal is moving down
            if corners[i][1] < corners[i+1][1]:
                Yvals = range(int(corners[i][1]+1), int(corners[i+1][1]+1))
                for val in Yvals:
                    coord = (corners[i][0], val)
                    full_path.append(coord)
            #animal is moving up
            else:
                Yvals = range(int(corners[i+1][1]), int(corners[i][1]))
                subPath = []
                for val in Yvals:
                    coord = (corners[i][0], val)
                    subPath = [coord] + subPath
                full_path.extend(subPath)
    return full_path

################################################################################
################################################################################

class Game:
    def __init__(self, game_info):
        """Initializes the game.

        `game_info` is a dictionary formatted in the following manner:
          { 'width': The width of the game grid, in an integer (i.e. number of pixels).
            'height': The height of the game grid, in an integer (i.e. number of pixels).
            'rocks': The set of tuple rock coordinates.
            'path_corners': An ordered list of coordinate tuples. The first
                            coordinate is the starting point of the path, the
                            last point is the end point (both of which lie on
                            the edges of the gameboard), and the other points
                            are corner ("turning") points on the path.
            'money': The money balance with which the player begins.
            'spawn_interval': The interval (in timesteps) for spawning animals
                              to the game.
            'animal_speed': The magnitude of the speed at which the animals move
                            along the path, in units of grid distance traversed
                            per timestep.
            'num_allowed_unfed': The number of animals allowed to finish the
                                 path unfed before the player loses.
          }
        """
        self.width, self.height = game_info['width'], game_info['height']
        self.path = game_info['path_corners']
        self.path_start = self.path[0]
        self.money = game_info['money']
        self.spawn_time = game_info['spawn_interval']
        self.animal_speed = game_info['animal_speed']
        self.lives_left = game_info['num_allowed_unfed']
        self.time = 0
        self.status = 'ongoing'
        self.clicked = None #name of selected zookeeper
        self.formations = []
        self.rocks = game_info['rocks']
        for rock in self.rocks:
            self.formations.append({'loc':rock, 'texture':Constants.TEXTURES['rock'], \
                                    'size':(Constants.ROCK_WIDTH, Constants.ROCK_HEIGHT)})
        self.animals = [] #list of Animal objects
        self.food = [] #list of Food objects
        self.keepers = [] #list of Keeper objects

    def render(self):
        """Renders the game in a form that can be parsed by the UI.

        Returns a dictionary of the following form:
          { 'formations': A list of dictionaries in any order, each one
                          representing a formation. Each dictionary is of the form
                            `{'loc': (x, y),
                              'texture': texture,
                              'size': (width, height)}`
                          where `(x,y)` is the center coordinate of the formation,
                          `texture` is its texture, and it has `width` and `height`
                          dimensions. The dictionary should contain the
                          formations of all animals, zookeepers, rocks, and food.
            'money': The amount of money the player has available.
            'status': The current state of the game which can be 'ongoing' or 'defeat'.
            'num_allowed_remaining': The number of animals which are still
                                     allowed to exit the board before the game
                                     status is `'defeat'`.
          }
        """
        formations = self.formations.copy()
        for animal in self.animals:
            formations.append({'loc':animal.location, 'texture':Constants.TEXTURES['animal'], \
                                    'size':(animal.width, animal.height)})
        for item in self.food:
            formations.append({'loc':item.location, 'texture':Constants.TEXTURES['food'], \
                                    'size':(item.width, item.height)})
        return {'formations':formations, 'money': self.money, 'status':self.status, \
                'num_allowed_remaining':self.lives_left}
            
    def timestep(self, mouse=None):
        """Simulates the evolution of the game by one timestep.

        In this order:
            (0. Do not take any action if the player is already defeated.)
            1. Compute any changes in formation locations, and remove any
                off-board formations.
            2. Handle any food-animal collisions, and remove the fed animals
                and eaten food.
            3. Throw new food if possible.
            4. Spawn a new animal from the path's start if needed.
            5. Handle mouse input, which is the integer coordinate of a player's
               click, the string label of a particular zookeeper type, or `None`.
            6. Redeem one unit money per animal fed this timestep.
            7. Check for the losing condition to update the game status if needed.
        """
        if self.status == 'defeat':
            return
        
        #change formation locations
        for animal in self.animals.copy():
            animal.update_loc()
            if not self.in_bounds(animal.location):
                self.animals.remove(animal)
                self.lives_left -= 1
        for item in self.food.copy():
            item.update_loc()
            if not self.in_bounds(item.location):
                self.food.remove(item)
        
        #handle collisions
        fed_num = 0
        for animal in self.animals.copy():
            fed = False
            for food in self.food.copy():
                if animal.is_fed(food):
                    self.food.remove(food)
                    if not fed:
                        fed = True
            if fed:
                self.animals.remove(animal)
                fed_num += 1
        
        #throw new food
        for keeper in self.keepers:
            newfood = keeper.throw_food(self.animals)
            if newfood is not None:
                self.food.append(newfood)
        
        #spawn new animals if needed
        if self.time % self.spawn_time == 0:
            newanimal = Animal(self.path_start, self.path, self.animal_speed)
            self.animals.append(newanimal)
            
        #handle mouse input
        if type(mouse) == str:
            self.clicked = mouse
        elif type(mouse) == tuple and self.clicked is not None:
            if self.money >= Constants.KEEPER_INFO[self.clicked]['price']:
                if self.in_bounds(mouse) and not self.on_path(mouse) and not self.is_occupied(mouse):
                    newkeeper = Keeper(mouse, self.clicked)
                    self.keepers.append(newkeeper)
                    self.formations.append({'loc':newkeeper.location, 'texture':newkeeper.texture, \
                                        'size':(newkeeper.width, newkeeper.height)})
                    self.money -= Constants.KEEPER_INFO[self.clicked]['price']
                    self.clicked = None
            else:
                raise NotEnoughMoneyError 
                
        #update money
        self.money += fed_num
        
        #check game status
        if self.lives_left < 0:
            self.status = 'defeat'
        
        if self.status == 'ongoing':
            self.time += 1
        
    def in_bounds(self, coord):
        """Checks if a coordinate is on the game board. Returns a Boolean."""
        x, y = coord[0], coord[1]
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return False
        return True
            
    def is_occupied(self, coord):
        """Checks if placing a zookeeper at a coordinate would overlap with 
        a rock or zookeeper. Returns a Boolean."""
        x, y = coord[0], coord[1]
        halfKeeperWidth, halfKeeperHeight = (Constants.KEEPER_WIDTH-1)//2, (Constants.KEEPER_HEIGHT-1)//2
        Xrange = range(x-halfKeeperWidth+1, x+halfKeeperWidth)
        Yrange = range(y-halfKeeperHeight+1, y+halfKeeperHeight)
        
        #check if zookeepers overlap
        for keeper in self.keepers:
            x, y = keeper.location[0], keeper.location[1]
            if x - halfKeeperWidth in Xrange or x + halfKeeperWidth in Xrange or x in Xrange:
                if y - halfKeeperHeight in Yrange or y + halfKeeperHeight in Yrange or y in Yrange:
                    return True
        
        #check if rocks overlap
        halfRockWidth, halfRockHeight = (Constants.ROCK_WIDTH-1)//2, (Constants.ROCK_HEIGHT-1)//2
        for rock in self.rocks:
            x, y = rock[0], rock[1]
            if x - halfRockWidth in Xrange or x + halfRockWidth in Xrange or x in Xrange:  
                if y - halfRockHeight in Yrange or y + halfRockHeight in Yrange or y in Yrange:
                    return True
        
        #if no overlaps, coordinated isn't occupied
        return False

    def on_path(self, coord):
        """Checks if a coordinate is on the path. Returns a Boolean."""
        x, y = coord[0], coord[1]
        halfKeeperWidth, halfKeeperHeight = (Constants.KEEPER_WIDTH-1)//2, (Constants.KEEPER_HEIGHT-1)//2
        path = get_path(self.path)
        halfThickness = (Constants.PATH_THICKNESS-1)//2
        for point in path:
            if (x-halfKeeperWidth >= point[0]-halfThickness and x-halfKeeperWidth <= point[0]+halfThickness) \
            or (x+halfKeeperWidth  >= point[0]-halfThickness and x+halfKeeperWidth <= point[0]+halfThickness) \
            or (x  >= point[0]-halfThickness and x <= point[0]+halfThickness):
                if (y-halfKeeperHeight >= point[1]-halfThickness and y-halfKeeperHeight <= point[1]+halfThickness) \
                or (y+halfKeeperHeight >= point[1]-halfThickness and y+halfKeeperHeight <= point[1]+halfThickness) \
                or (y >= point[1]-halfThickness and y <= point[1]+halfThickness):
                    return True
        return False 
        
################################################################################
################################################################################
# Aditional Classes.
        
class Formations:
    def __init__(self, location):
        self.location = location
    
class Animal(Formations):
    def __init__(self, location, path, speed):
        Formations.__init__(self, location)
        self.width = Constants.ANIMAL_WIDTH
        self.height = Constants.ANIMAL_HEIGHT
        self.texture = Constants.TEXTURES['animal']
        self.speed = speed
        self.last_path_corner = path[0] #coord in form (x,y)
        self.path = path[1:] #list of coords in form (x,y)
        
    def update_loc(self, move=None):
        """Updates animal location each timestep. Returns nothing."""
        #if the animal has already walked the entire path
        if len(self.path) == 0:
            self.location = (-100, -100)
            return
        
        if move == None:
            move = self.speed
        dis = distance(self.location, self.path[0])
        
        #move exits end of path
        if len(self.path) == 1 and move > dis:
            self.location = (-100,-100)
            
        #move is straight
        elif move < dis:
            if self.last_path_corner[0] == self.path[0][0]:
                #move up
                if self.last_path_corner[1] > self.path[0][1]:
                    self.location = (self.location[0], int(self.location[1] - move))                    
                #move down
                else:
                    self.location = (self.location[0], int(self.location[1] + move))
            else:
                #move left
                if self.last_path_corner[0] > self.path[0][0]:
                    self.location = (int(self.location[0] - move), self.location[1])
                #move right
                else:
                    self.location = (int(self.location[0] + move), self.location[1])
        
        #move passes/reaches a corner
        else:
            self.location = self.path[0]
            self.last_path_corner = self.path[0]
            self.path = self.path[1:]
            if move > dis:
                self.update_loc(move-dis)
                
    def is_fed(self, food):
        """Determines if collision between animal and food. Returns a Boolean.
        `food` is a Food object."""
        halfAnimalWidth, halfAnimalHeight = (self.width)/2, (self.height)/2
        corner1 = (self.location[0]-halfAnimalWidth, self.location[1]-halfAnimalHeight)
        corner2 = (self.location[0]+halfAnimalWidth, self.location[1]+halfAnimalHeight)
        
        halfFoodWidth, halfFoodHeight = (food.width)/2, (food.height)/2
        tl = (food.location[0]-halfFoodWidth, food.location[1]-halfFoodHeight)
        br = (food.location[0]+halfFoodWidth, food.location[1]+halfFoodHeight)
        if (tl[0] > corner1[0] and tl[0] < corner2[0]) or (br[0] > corner1[0] and br[0] < corner2[0]):
            if (tl[1] > corner1[1] and tl[1] < corner2[1]) or (br[1] > corner1[1] and br[1] < corner2[1]):
                return True
        return False 
            
class Food(Formations):
    def __init__(self, location, Xspeed, Yspeed):
        Formations.__init__(self, location)
        self.width = Constants.FOOD_WIDTH
        self.height = Constants.FOOD_HEIGHT
        self.texture = Constants.TEXTURES['food']
        self.Xspeed, self.Yspeed = Xspeed, Yspeed
        
    def update_loc(self):
        """Updates food location each timestep. Returns nothing."""
        x, y = self.location[0], self.location[1]
        self.location = (x + self.Xspeed, y + self.Yspeed)
        
class Keeper(Formations):
    def __init__(self, location, keeper_type):
        Formations.__init__(self, location)
        self.texture = Constants.TEXTURES[keeper_type]
        self.width = Constants.KEEPER_WIDTH
        self.height = Constants.KEEPER_HEIGHT
        self.throwSpeed = Constants.KEEPER_INFO[keeper_type]['throw_speed_mag']
        self.range = Constants.KEEPER_INFO[keeper_type]['range']
        
    def throw_food(self, animals):
        """Creates and returns a new food object if an animal is in range."""
        #animals is in order of decreasing 'hunger' (spawn order)
        for animal in animals:
            if self.in_range(animal):
                bestTime = None
                bestCoord = None
                corners = [animal.location] + animal.path
                path = get_path(corners)
                #for each coordinate in path, calculate the time the animal and
                #food would take to get there
                for i, coord in enumerate(path):
                    animal_time = (i+1)/animal.speed
                    food_time = distance(self.location, coord)/self.throwSpeed
                    time = abs(animal_time - food_time)
                    #store the coordinate with the smallest difference 
                    #between food time and animal time
                    if bestTime is None:
                        bestTime, bestCoord = time, coord
                    elif time < bestTime:
                        bestTime, bestCoord = time, coord
                if bestCoord is not None:
                    Xspeed = (bestCoord[0] - self.location[0])/distance(self.location, bestCoord)*self.throwSpeed
                    Yspeed = (bestCoord[1] - self.location[1])/distance(self.location, bestCoord)*self.throwSpeed
                    return Food(self.location, Xspeed, Yspeed)
        return None
    
    def in_range(self, animal):
        if distance(self.location, animal.location) <= self.range:
            return True
        return False     

################################################################################
################################################################################

if __name__ == '__main__':
    pass