"""
Author: Hector Lovo
Created on: 5/3/2015

This dungeon generator was created as a demo for WillowTreeApps.
"""
from pygame.constants import *
from pygame import Rect
import random
import os
import pygame

map_theme = {
    0: {
        "lst_image": ['tomb.png', 'table.png'],
        "floor": "floor.png",
        "drk_floor": "drk_floor.png",
        "wall": "brick_wall.png",
        "drk_wall": "drk_brick_wall.png",
        "stairs_down": "stairs_down.png",
        "drk_stairs_down": "drk_stairs_down.png",
        "stairs_up": "stairs_up.png",
        "drk_stairs_up": "drk_stairs_up.png"
    },
    1: {
        "lst_image": ['tomb.png', 'rock.png'],
        "floor": "grass.png",
        "drk_floor": "drk_grass.png",
        "wall": "bush.png",
        "drk_wall": "drk_bush.png",
        "stairs_down": "stairs_down.png",
        "drk_stairs_down": "drk_stairs_down.png",
        "stairs_up": "stairs_up.png",
        "drk_stairs_up": "drk_stairs_up.png"
    },
    2: {
        "lst_image": ['tomb.png', 'rock.png'],
        "floor": "sand.png",
        "drk_floor": "drk_sand.png",
        "wall": "cactus.png",
        "drk_wall": "drk_cactus.png",
        "stairs_down": "stairs_down.png",
        "drk_stairs_down": "drk_stairs_down.png",
        "stairs_up": "stairs_up.png",
        "drk_stairs_up": "drk_stairs_up.png"
    }
}

# constants
PLAYER_FACING_UP = 0
PLAYER_FACING_LEFT = 1
PLAYER_FACING_DOWN = 2
PLAYER_FACING_RIGHT = 3

PLAYER_FOV_DIST = 6


class Entity(pygame.sprite.Sprite):
    """
    Represents any object/entity on the map.
    """

    def __init__(self, left, top, img_file_name, colorkey=None):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img_file_name, colorkey)
        self.rect.left = left
        self.rect.top = top


class Tile(Entity):
    """
    This class represents all the "tiles" on the map: walls/floors/stairs/etc.
    """

    def __init__(self, left, top, img_file_name, img_file_dark, blocked, block_sight=None, colorkey=None):
        super(Tile, self).__init__(left, top, img_file_name, colorkey)
        self.drk_image, _ = load_image(img_file_dark, colorkey)
        self.blocked = blocked
        self.visited = False
        if block_sight is None:
            self.block_sight = blocked
        else:
            self.block_sight = block_sight


class AestheticObject(Tile):
    """
    This class represents the objects on the map: tombs/desks/rocks/etc; as tiles.
    """

    def __init__(self, left, top, theme_num):
        lst_image = map_theme[theme_num]["lst_image"]
        image = random.choice(lst_image)
        super(AestheticObject, self).__init__(left, top, image, 'drk_' + image, blocked=True, block_sight=False,
                                              colorkey=-1)


class Floor(Tile):
    """
    This class represents a floor tile.
    """

    def __init__(self, left, top, theme_num):
        super(Floor, self).__init__(left, top, map_theme[theme_num]["floor"], map_theme[theme_num]["drk_floor"],
                                    blocked=False)


class Wall(Tile):
    """
    This class represents a wall tile.
    """

    def __init__(self, left, top, theme_num):
        super(Wall, self).__init__(left, top, map_theme[theme_num]["wall"], map_theme[theme_num]["drk_wall"],
                                   blocked=True)


class Stairs(Tile):
    """
    This class represents the staircase on the map.
    """

    def __init__(self, left, top, is_up, theme_num):
        super(Stairs, self).__init__(left, top, map_theme[theme_num]["stairs_down"],
                                     map_theme[theme_num]["drk_stairs_down"],
                                     blocked=True,
                                     block_sight=False)
        # upstairs
        if is_up:
            self.image, _ = load_image(str(map_theme[theme_num]["stairs_up"]), -1)
            self.drk_image, _ = load_image(str(map_theme[theme_num]["drk_stairs_up"]), -1)


class Key(Entity):
    """
    This class represents the keys on the map.
    """

    def __init__(self, left, top):
        super(Key, self).__init__(left, top, 'key.png', colorkey=-1)
        self.drk_image, _ = load_image('drk_key.png', -1)
        self.visited = False
        self.block_sight = False


class Room(object):
    """
    This class represents the rooms on the map.
    """

    def __init__(self, left, top, width, height):
        self.dimension = Rect(left * 32, top * 32, width * 32, height * 32)


class EmptySprite(pygame.sprite.Sprite):
    """
    This object is used to represent dummy-entities. It is used when determining collisions
    with other entities.
    """

    def __init__(self, rect):
        self.rect = rect


class SpriteSheet(object):
    """
    This class enables the sprites to be animated.
    """

    def __init__(self, filename):
        self.sheet, _ = load_image(filename)

    def image_at(self, rectangle, colorkey=None):
        """
        Loads image from x,y,x+offset,y+offset
        :param rectangle:
        :param colorkey:
        :return:
        """
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """
        Loads the images and returns them as a list.
        :param rects: (Rect) holds the x-y coordinates, height, and width
        :param colorkey: determines which color to make transparent
        :return: (list) of images
        """
        return [self.image_at(rect, colorkey) for rect in rects]


class Enemy(pygame.sprite.Sprite):
    """
    This class is not fully implemented. This will represent an enemy NPC and it should
    be similar to the Player class.
    """

    def __init__(self, left, top, img_file_name):
        super(Enemy, self).__init__(left, top, img_file_name)


class Player(pygame.sprite.Sprite):
    """
    This class represents the main player.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # TODO: speed should be 4; change offsets based around 4 (instead of 8)
        self.radius = PLAYER_FOV_DIST << 5
        # steps to move
        self.dx = 4
        self.dy = 4
        # used for animation
        self.frames = 9
        self.frames_row = 4
        self.elapsed_frames = 0
        player_sprites = SpriteSheet("player_walk_sprite.png")
        self.images_lst = list()
        for x in range(self.frames_row):
            tuple_lst = list()
            for frame in range(self.frames):
                tuple_lst.append((frame << 5, x << 5, 32, 32))
            sprite_row = player_sprites.images_at(tuple_lst, colorkey=-1)
            self.images_lst.append(sprite_row)
        self.img_frame_num = 0
        # init image
        self.image = self.images_lst[PLAYER_FACING_DOWN][0]
        # init rect
        self.rect = self.image.get_rect()

    def move(self, my_map, other_objs, key):
        """
        Moves the player around the map. Determines if the player is colliding with a wall,
         is able to pick up a key, and if is able to go on to the next level.
        :param my_map: (map) holds map data
        :param other_objs: (list) objects that cannot be traversed through: tombs/rocks/desks/etc.
        :param key: (list) keys to collect
        """
        # used for detecting collision
        x_move = 0
        y_move = 0
        offset_x = 0
        offset_y = 0
        # initial direction to face-in
        facing = PLAYER_FACING_DOWN

        if key == K_RIGHT:
            x_move = self.dx
            offset_x = 16
            offset_y = 12
            facing = PLAYER_FACING_RIGHT
        elif key == K_LEFT:
            x_move = -self.dx
            offset_x = 12
            offset_y = 12
            facing = PLAYER_FACING_LEFT
        elif key == K_UP:
            y_move = -self.dy
            offset_x = 12
            offset_y = 12
            facing = PLAYER_FACING_UP
        elif key == K_DOWN:
            y_move = self.dy
            offset_y = 16
            offset_x = 12
        # player animation
        if self.img_frame_num < self.frames - 1:
            if self.elapsed_frames > 1:
                self.img_frame_num += 1
                self.elapsed_frames = -1
        else:
            self.img_frame_num = 0
        self.elapsed_frames += 1
        self.image = self.images_lst[facing][self.img_frame_num]
        # player object collision detection
        obj_collision = False
        x_val = self.rect.x + x_move + offset_x
        y_val = self.rect.y + y_move + offset_y
        dummy_sprite = EmptySprite(Rect(x_val, y_val, 4, 8))
        for obj in other_objs:
            obj_collision = pygame.sprite.collide_rect(dummy_sprite, obj)
            if obj_collision:
                break
        # determine if player can move in x-y direction
        if not my_map[(self.rect.y + y_move + offset_y) >> 5][(self.rect.x + x_move + offset_x) >> 5].blocked and \
                not obj_collision:
            self.rect.move_ip(x_move, y_move)


def load_image(name, colorkey=None):
    """
    This method loads an image from the data.images dir and creates a
    pixel-bit-map image from it.
    :param name: of image file
    :type name: str
    :param colorkey: to make transparent
    :type colorkey: -1 or some rgb-color
    :return: pixel-bit image, rectangle
    :rtype: pixel-bit image, Rectangle
    """
    fullname = os.path.join('data', 'images')
    fullname = os.path.join(fullname, name)
    image = None
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        exit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()
