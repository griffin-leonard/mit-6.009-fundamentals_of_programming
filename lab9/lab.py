"""6.009 Spring 2019 Lab 9 -- 6.009 Zoo"""

from math import ceil  # ONLY import allowed in this lab

# NO CUSTOM IMPORTS ALLOWED!

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

    # some other characters
    DEMON_WIDTH = 51
    DEMON_HEIGHT = 51
    DEMON_RADIUS = 75  # Only animals this close are affected.
    DEMON_MULTIPLIER = 2  # Animal speeds multiplied by this factor
    DEMON_PRICE = 100

    VHS_WIDTH = 31
    VHS_HEIGHT = 31
    VHS_RADIUS = 75
    VHS_MULTIPLIER = .5
    VHS_PRICE = 20

    CRAZY_NAP_LENGTH = 20

    TRAINEE_THRESHOLD = 20  # How many food hits must the trainee score,
    # before becoming a speedy zookeeper?
    
    SNOWBALL_MULTIPLIER = .5
    FREEZE_TIME = 40

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'OverreachingZookeeper': '1f477',
        'food': '1f34e',
        'Demon': '1f479',
        'VHS': '1f4fc',
        'TraineeZookeeper': '1f476',
        'CrazyZookeeper': '1f61c',
        'SleepingZookeeper': '1f634',
        'FreezeZookeeper': '1f385',
        'snowball': '2744'
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
                        'throw_speed_mag': 5},
                   'TraineeZookeeper':
                       {'price': 50,
                        'range': 100,
                        'throw_speed_mag': 5},
                   'CrazyZookeeper':
                       {'price': 100,
                        'range': 1000,
                        'throw_speed_mag': 50},
                   'FreezeZookeeper':
                        {'price': 100,
                         'range': 200,
                         'throw_speed_mag': 30}
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
        self.speedmods = [] #list of SpeedMod objects
        self.specialKeepers = []

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
        for keeper in self.specialKeepers.copy():
            formations.append({'loc':keeper.location, 'texture':keeper.texture, \
                                        'size':(keeper.width, keeper.height)})
            #if a trainee zookeeper has been upgraded, remove it from specialKeepers
            if keeper.keeper_type == 'SpeedyZookeeper':
                self.formations.append({'loc':keeper.location, 'texture':keeper.texture, \
                                        'size':(keeper.width, keeper.height)})
                self.specialKeepers.remove(keeper)
        for item in self.food:
            formations.append({'loc':item.location, 'texture':item.texture, \
                                    'size':(item.width, item.height)})
        return {'formations':formations, 'money': self.money, 'status':self.status, \
                'num_allowed_remaining':self.lives_left}
            
    def timestep(self, mouse=None):
        """Simulates the evolution of the game by one timestep.

        In this order:
             (0. Do not take any action if the player is already defeated.)
             1. Compute the new speed of animals based on the presence of nearby VHS cassettes or demons.
             2. Compute any changes in formation locations and remove any off-board formations.
             3. Handle any food-animal collisions, and remove the fed animals and the eaten food.
             4. Upgrade trainee zookeeper if needed.
             5. Throw new food if possible.
             6. Spawn a new animal from the path's start if needed.
             7. Handle mouse input, which is the integer tuple coordinate of a player's click, the string label of a particular
               zookeeper type, or None.
             8. Redeem one dollar per animal fed this timestep.
             9. Check for the losing condition.
        """
        if self.status == 'defeat':
            return
        
        #change animal speeds with VHS and Demons
        for animal in self.animals:
            animal.speed = self.animal_speed
            if animal.frozen:
                animal.speed *= Constants.SNOWBALL_MULTIPLIER
        for speedmod in self.speedmods:
            speedmod.change_speed(self.animals)
        for animal in self.animals:
            animal.speed = ceil(animal.speed)
        
        #change formation locations
        for animal in self.animals.copy():
            animal.update_loc()
            if not self.in_bounds(animal.location):
                self.animals.remove(animal)
                self.lives_left -= 1
            if animal.frozen:
                if animal.freeze_count > 0:
                    animal.freeze_count -= 1
                else:
                    animal.frozen = False
        for item in self.food.copy():
            item.update_loc()
            if not self.in_bounds(item.location):
                self.food.remove(item)
        
        #handle collisions
        fed_num = 0
        used_food = set([])
        for animal in self.animals.copy():
            fed = False
            for food in self.food:
                if animal.is_fed(food):
                    if food.keeper.keeper_type == 'TraineeZookeeper':
                        food.keeper.train_threshold -= 1
                    if not fed and food.proj_type == 'apple':
                        fed = True
                    elif animal.freeze_count != Constants.FREEZE_TIME and food.proj_type == 'snow':
                        animal.speed *= Constants.SNOWBALL_MULTIPLIER
                        animal.freeze_count = Constants.FREEZE_TIME
                        animal.frozen = True
                    used_food.add(food)
            if fed:
                self.animals.remove(animal)
                fed_num += 1
        for item in used_food:
            self.food.remove(item)
                
        #upgrade trainees
        for keeper in self.keepers.copy():
            if keeper.train_threshold <= 0:
                keeper.keeper_type = 'SpeedyZookeeper'
                keeper.texture = Constants.TEXTURES['SpeedyZookeeper']
                keeper.throwSpeed = Constants.KEEPER_INFO['SpeedyZookeeper']['throw_speed_mag']
                keeper.range = Constants.KEEPER_INFO['SpeedyZookeeper']['range']
        
        #throw new food
        for keeper in self.keepers:
            if keeper.keeper_type == 'CrazyZookeeper':
                if  keeper.texture == Constants.TEXTURES['CrazyZookeeper']:
                    newfood = keeper.throw_food(self.animals)
                    if newfood is not None:
                        keeper.nap_count += 1
                        keeper.texture = Constants.TEXTURES['SleepingZookeeper']
                else:
                    if keeper.nap_count % (Constants.CRAZY_NAP_LENGTH+1) == Constants.CRAZY_NAP_LENGTH:
                        keeper.texture = Constants.TEXTURES['CrazyZookeeper']
                    newfood = None
                    keeper.nap_count += 1
            else:
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
            if self.clicked == 'VHS':
                price = Constants.VHS_PRICE
            elif self.clicked == 'Demon': 
                price = Constants.DEMON_PRICE
            else:
                price = Constants.KEEPER_INFO[self.clicked]['price']
            if self.money >= price:
                if self.in_bounds(mouse) and not self.is_occupied(mouse, self.clicked):
                    if self.clicked == 'VHS' or self.clicked == 'Demon':
                        newkeeper = SpeedMod(mouse, self.clicked)
                        self.speedmods.append(newkeeper)
                    else:
                        newkeeper = Keeper(mouse, self.clicked)
                        self.keepers.append(newkeeper)
                        
                    if self.clicked == 'TraineeZookeeper' or self.clicked == 'CrazyZookeeper':
                        self.specialKeepers.append(newkeeper)
                    else:
                        self.formations.append({'loc':newkeeper.location, 'texture':newkeeper.texture, \
                                        'size':(newkeeper.width, newkeeper.height)})
                    self.money -= price
                    self.clicked = None
            else:
                raise NotEnoughMoneyError 
                
        self.money += fed_num #update money
        if self.lives_left < 0: #check game status
            self.status = 'defeat'        
        if self.status == 'ongoing': #increment time
            self.time += 1
        
    def in_bounds(self, coord):
        """Checks if a coordinate is on the game board. Returns a Boolean."""
        x, y = coord[0], coord[1]
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return False
        return True
            
    def is_occupied(self, coord, keeper):
        """Checks if placing a zookeeper at a coordinate would overlap with 
        a rock, zookeeper, or the path. Returns a Boolean."""
        x, y = coord[0], coord[1]
        if keeper == 'VHS':
            halfKeeperWidth, halfKeeperHeight = (Constants.VHS_WIDTH-1)//2, (Constants.VHS_HEIGHT-1)//2
        elif keeper == 'Demon':
            halfKeeperWidth, halfKeeperHeight = (Constants.DEMON_WIDTH-1)//2, (Constants.DEMON_HEIGHT-1)//2
        else:
            halfKeeperWidth, halfKeeperHeight = (Constants.KEEPER_WIDTH-1)//2, (Constants.KEEPER_HEIGHT-1)//2
        
        #check if path overlaps
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
                
        Xrange = range(x-halfKeeperWidth+1, x+halfKeeperWidth)
        Yrange = range(y-halfKeeperHeight+1, y+halfKeeperHeight)
        #check if speedmods overlap
        for speedmod in self.speedmods:
            halfKeeperWidth, halfKeeperHeight = (speedmod.width-1)//2, (speedmod.height-1)//2
            x, y = speedmod.location[0], speedmod.location[1]
            if x - halfKeeperWidth in Xrange or x + halfKeeperWidth in Xrange or x in Xrange:
                if y - halfKeeperHeight in Yrange or y + halfKeeperHeight in Yrange or y in Yrange:
                    return True

        #check if zookeepers overlap
        halfKeeperWidth, halfKeeperHeight = (Constants.KEEPER_WIDTH-1)//2, (Constants.KEEPER_HEIGHT-1)//2
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
        self.freeze_count = 0
        self.frozen = False
        
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
    def __init__(self, location, Xspeed, Yspeed, keeper):
        Formations.__init__(self, location)
        self.width = Constants.FOOD_WIDTH
        self.height = Constants.FOOD_HEIGHT
        if keeper.keeper_type == 'FreezeZookeeper':
            self.texture = Constants.TEXTURES['snowball']
            self.proj_type = 'snow'
        else:
            self.texture = Constants.TEXTURES['food']
            self.proj_type = 'apple'
        self.Xspeed, self.Yspeed = Xspeed, Yspeed
        self.keeper = keeper
        
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
        self.keeper_type = keeper_type
        self.train_threshold = Constants.TRAINEE_THRESHOLD
        self.nap_count = 0
        
    def throw_food(self, animals):
        """Creates and returns a new food object if an animal is in range."""
        #animals is in order of decreasing 'hunger' (spawn order)
        for animal in animals:
            if self.keeper_type == 'FreezeZookeeper' and animal.frozen:
                pass
            elif distance(self.location, animal.location) <= self.range:
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
                    return Food(self.location, Xspeed, Yspeed, self)
        return None                
    
class SpeedMod(Formations):
    def __init__(self, location, charType):
        Formations.__init__(self, location)
        self.texture = Constants.TEXTURES[charType]
        if charType == 'VHS':
            self.width = Constants.VHS_WIDTH
            self.height = Constants.VHS_HEIGHT
            self.range = Constants.VHS_RADIUS
            self.speedFactor = Constants.VHS_MULTIPLIER
        elif charType == 'Demon':
            self.width = Constants.DEMON_WIDTH
            self.height = Constants.DEMON_HEIGHT
            self.range = Constants.DEMON_RADIUS
            self.speedFactor = Constants.DEMON_MULTIPLIER
            
    def change_speed(self, animals):
        """Modifies the speed of every animal entering and leaving range."""
        for animal in animals:
            dis = distance(self.location, animal.location)
            if dis <= self.range:
                    animal.speed = animal.speed * self.speedFactor
            
################################################################################
################################################################################

if __name__ == '__main__':
    pass