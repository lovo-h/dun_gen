"""
Author: Hector Lovo
Created on: 5/3/2015

This dungeon generator was created as a demo for WillowTreeApps.
"""
from entities import Wall, Floor, Room, Stairs, Key, AestheticObject, Enemy, map_theme
import random
from pygame.sprite import Group


class TheMap(object):
    """
    This class holds the landscape of the map and other relevant information.
    """

    def __init__(self, width=40, height=40):
        self.theme_num = random.randint(0, len(map_theme) - 1)
        self.landscape = [[Wall(x * 32, y * 32, self.theme_num) for x in range(width + 1)] for y in range(height + 1)]
        self.width = len(self.landscape[0]) - 1
        self.height = len(self.landscape) - 1
        self.player_start_loc = None
        self.map_objects = {"other": Group(), "stairs": Group(), "keys": Group()}
        self.enemies_lst = Group()
        self.probability_enemy_appears = 0
        self.initialize()

    def create_room(self, room):
        """
        Creates a room, given some coordinates and dimensions.
        :param room: (room object) holds x-y coordinates, height, and width of the room
        """
        # go through the tiles in the rectangle and make them passable
        x1 = room.dimension.x >> 5
        x2 = (room.dimension.x + room.dimension.width) >> 5
        y1 = room.dimension.y >> 5
        y2 = (room.dimension.y + room.dimension.height) >> 5
        for x in range(x1, x2):
            for y in range(y1, y2):
                self.landscape[y][x] = Floor(x << 5, y << 5, self.theme_num)
        # light up the walls containing this room
        for x in range(x1, x2):
            self.landscape[y1 - 1][x].block_sight = False
            self.landscape[y2][x].block_sight = False
        for y in range(y1, y2):
            self.landscape[y][x1 - 1].block_sight = False
            self.landscape[y][x2].block_sight = False

    def add_stairs(self, room):
        """
        Places staircase in some room on the map.
        :param room: (room object) holds x-y coordinates, height, and width of the room
        """
        (x, y) = get_valid_room_coords(room)
        stairs = Stairs(x, y, is_up=random.randint(0, 1), theme_num=self.theme_num)
        self.map_objects["stairs"].add(stairs)

    def add_keys(self, room):
        """
        Places keys in some room on the map.
        :param room: (room object) holds x-y coordinates, height, and width of the room
        """
        (x, y) = get_valid_room_coords(room)
        keys = Key(x, y)
        self.map_objects["keys"].add(keys)

    def add_aesthetic_obj(self, room):
        """
        Places objects in some room on the map.
        :param room: (room object) holds x-y coordinates, height, and width of the room
        """
        (x, y) = get_valid_room_coords(room)
        obj = AestheticObject(x, y, self.theme_num)
        self.map_objects["other"].add(obj)

    def add_enemies(self, room):
        """
        Places enemy in some room on the map that contains a key.
        :param room: (room object) holds x-y coordinates, height, and width of the room
        """
        (x, y) = get_valid_room_coords(room)
        enemy = Enemy(x, y)
        self.enemies_lst.add(enemy)

    def generate_rooms_around_map(self, rooms):
        """
        Generates a bunch of rooms and places them on the map if they do not
        collide with each other.
        :param rooms: (list) will hold the rooms generated
        """
        room_tries = len(self.landscape) * len(self.landscape[0]) >> 6  # times to try to create room: area / 64
        max_room_dimension = max(5, room_tries >> 2)  # max-room-dimension: max(5, area / 256)
        if max_room_dimension > 14:  # bound of room dimension: 14
            max_room_dimension = 14
        for n in range(room_tries):
            failed = False
            w = random.randint(4, max_room_dimension)
            h = random.randint(4, max_room_dimension)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            current_room = Room(x, y, w, h)
            for other_room in rooms:
                current_room_adjusted = Room(x - 1, y - 1, w + 1, h + 1)
                if current_room_adjusted.dimension.colliderect(other_room.dimension):
                    failed = True
                    break
            if not failed:
                self.create_room(current_room)
                (curr_cent_x, curr_cent_y) = current_room.dimension.center
                room_count = len(rooms)
                if room_count == 0:
                    # set the player's start location
                    self.player_start_loc = (curr_cent_x, curr_cent_y)
                elif room_count > 0:
                    # create halls between rooms
                    (prev_cent_x, prev_cent_y) = rooms[room_count - 1].dimension.center
                    prev_cent_x >>= 5  # divide by 32 -> cell-representation
                    prev_cent_y >>= 5
                    curr_cent_y >>= 5
                    curr_cent_x >>= 5
                    # randomly decide whether to draw halls vert-first or horz-first
                    if random.randint(0, 1) == 0:
                        self.create_h_hall(prev_cent_x, curr_cent_x, prev_cent_y)
                        self.create_v_hall(prev_cent_y, curr_cent_y, curr_cent_x)
                    else:
                        self.create_v_hall(prev_cent_y, curr_cent_y, prev_cent_x)
                        self.create_h_hall(prev_cent_x, curr_cent_x, curr_cent_y)
                rooms.append(current_room)
                # place some aesthetic in the room
                if random.randint(0, 2) == 1:
                    self.add_aesthetic_obj(current_room)

    def initialize(self):
        """
        Initializes the map:
            - places a random configuration of rooms on the map.
            - places a spot for the player to start from
            - places the keys on the map
            - probably places a guard near the key; depends on probability
        """
        rooms = list()
        self.generate_rooms_around_map(rooms)
        # place the exit randomly
        indx = random.randrange(len(rooms))
        some_room = rooms.pop(indx)
        self.add_stairs(some_room)
        # put nothing where player begins
        rooms.pop(0)
        # how many keys to place: try 4 or more, else: however many rooms exist
        if len(rooms) > 3:
            placeable_keys = random.randint(4, 8)
        else:
            placeable_keys = len(rooms)
        # place keys in rooms, around map
        for x in range(0, placeable_keys):
            indx = random.randrange(len(rooms))
            some_room = rooms.pop(indx)
            self.add_keys(some_room)
            # add a guard
            if random.randint(0, 20 - self.probability_enemy_appears) < 5:  # init: 20% probability
                self.add_enemies(some_room)

    def create_h_hall(self, pcx, ncx, pcy):
        """
        Creates the horizontal hallway from room-A to room-B. Also, makes the
        hall's walls illuminable.
        :param pcx: (int) previous room's x-center coordinate
        :param ncx: (int) new room's x-center coordinate
        :param pcy: (int) previous room's y-center coordinate
        """
        for x in range(min(pcx, ncx), max(pcx, ncx) + 1):
            self.landscape[pcy][x] = Floor(x << 5, pcy << 5, self.theme_num)
            # allow walls to be illuminated
            self.landscape[pcy - 1][x].block_sight = False
            self.landscape[pcy + 1][x].block_sight = False

    def create_v_hall(self, pcy, ncy, pcx):
        """
        Creates the vertical hallway from room-A to room-B.  Also, makes the
        hall's walls illuminable.
        :param pcy: (int) previous room's y-center coordinate
        :param ncy: (int) new room's x-center coordinate
        :param pcx: (int) previous room's x-center coordinate
        """
        for y in range(min(pcy, ncy), max(pcy, ncy) + 1):
            self.landscape[y][pcx] = Floor(pcx << 5, y << 5, self.theme_num)
            # allow walls to be illuminated
            self.landscape[y][pcx + 1].block_sight = False
            self.landscape[y][pcx - 1].block_sight = False


def get_valid_room_coords(room):
    """
    Creates valid coordinates within the dimensions of some room
    :param room: (room object) holds x-y coordinates, height, and width of the room
    :return: (tuple) x-y coordinates from a random spot in the room
    """
    x1 = (room.dimension.x + 32) >> 5
    x2 = (room.dimension.x + room.dimension.width - 32) >> 5
    y1 = (room.dimension.y + 32) >> 5
    y2 = (room.dimension.y + room.dimension.height - 32) >> 5
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    return x << 5, y << 5