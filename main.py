"""
Dun-Gen
Author: Hector Lovo
Created on: 5/3/2015

This dungeon generator was created as a demo for WillowTreeApps.

Abstract:
    This dungeon generator creates a map by:
        - generating a map of "walls"
        - generates a random room with a random dimension
            - throws the room on the map
            - if the room does not intersect with another room, accept; otherwise, reject.
        - connects the previous room with the current room; unless it's the first room.
        - randomly selects a theme; based off of three selectable themes: found in ENTITIES.PY
        - finally, it places random objects, randomly, in a room: this does mean that there may be
          instances in which some pathway may be blocked. This is fixable by placing objects randomly
          in a room, in a dimension 1 size smaller.

    Initially, the entire map is blacked out and as the player traverses the map, the map's features are
    revealed. The radius of the light around the player may be changed in: ENTITIES.PY (PLAYER_FOV_DIST).
    Currently, it's set to a radius of 6.

    To generate a new map, simply press "s" key to skip. Otherwise, collect all the keys and find the stairs.
    If you press "s" to skip the map, the map will not increase in size by 2 units.
"""

from pygame.constants import *
from entities import Player
from camera import Camera, complex_camera
from map import TheMap
import pygame
import random

if not pygame.font:
    print 'Warning, fonts disabled'
if not pygame.mixer:
    print 'Warning, sound disabled'

LAND_WIDTH = 50
LAND_HEIGHT = 50

LOADING_MSG_FONT_SIZE = 36
RANDOM_LOADING_MSG_FONT_SIZE = 20
RANDOM_LOADING_MSGS = ["They are looking for you. Don't stop. Keep moving.",
                       "Some keys are hidden behind objects. Look out for them!",
                       "The more levels you complete, the more friends they bring.",
                       "It seems like the map is getting bigger... Is it?",
                       "Don't let them get you. One touch will put you to sleep."]


class DunGen:
    """
    This is the main class that initializes everything.
    """

    def __init__(self, width=1000, height=600):
        pygame.init()
        # set the window dimensions
        self.window_width = width
        self.window_height = height
        # create the screen
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        # noinspection PyArgumentList
        self.background = pygame.Surface((self.window_width, self.window_height))
        # generate the map
        self.map = TheMap(LAND_WIDTH, LAND_HEIGHT)
        # creates the clock
        self.clock = pygame.time.Clock()
        # init player
        self.player = Player()
        self.player.rect.left = self.map.player_start_loc[0]
        self.player.rect.top = self.map.player_start_loc[1]
        self.player_sprites = pygame.sprite.RenderPlain(self.player)
        # create the camera
        self.camera = Camera(complex_camera, self.map.width << 5, self.map.height << 5, self.window_width,
                             self.window_height)

    def controller(self):
        """
        Handles all of the events-functionality: keys-pressed, etc.
        """
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if (e.key == K_RIGHT) or (e.key == K_LEFT) or (e.key == K_UP) or (e.key == K_DOWN):
                    self.player.move(self.map.landscape, self.map.map_objects["other"], e.key)
                elif e.key == K_SPACE:
                    # determine if keys are around; remove the key if found
                    pygame.sprite.spritecollide(self.player, self.map.map_objects["keys"], True)
                    # determine if all keys have been collected and player's at a stairwell
                    if len(self.map.map_objects["keys"]) == 0 and pygame.sprite.spritecollide(self.player,
                                                                                              self.map.map_objects[
                                                                                                  "stairs"], False):
                        self.load_new_map()
                elif e.key == K_s:
                    self.map.width -= 2
                    self.map.height -= 2
                    self.load_new_map()
                elif e.key == K_ESCAPE:
                    quit()
            elif e.type == QUIT:
                quit()

    def load_new_map(self):
        """
        Loads a new map. Displays a loading message for 6 seconds and generates a new map.
        """
        self.clock.tick()  # initialize a counter
        self.screen.blit(self.background, (0, 0))
        self.display_text_to_screen(LOADING_MSG_FONT_SIZE, "Loading...")
        self.display_text_to_screen(RANDOM_LOADING_MSG_FONT_SIZE, random.choice(RANDOM_LOADING_MSGS),
                                    pos_y=(self.background.get_height() >> 1) + 35,
                                    rgb_color=(255, 25, 25))
        pygame.display.update()  # display loading page
        # generate a new game
        self.map = TheMap(self.map.width + 2, self.map.height + 2)
        self.player.rect.left, self.player.rect.top = self.map.player_start_loc
        self.camera = Camera(complex_camera, self.map.width << 5, self.map.height << 5,
                             self.window_width,
                             self.window_height)
        t1 = self.clock.tick()
        time_to_wait = 6000 - t1  # provide 6 seconds to read loading msg
        pygame.time.wait(time_to_wait)

    def display_text_to_screen(self, font_size, msg, pos_x=None, pos_y=None, rgb_color=(255, 255, 255)):
        """
        displays some text to the screen
        :param font_size: (int) font size
        :param msg: (str) message to display
        :param pos_x: (int) x-coordinate to display at
        :param pos_y: (int) y-coordinate to display at
        :param rgb_color: (tuple) (r,g,b)
        """
        if pygame.font:
            if not pos_x:
                pos_x = self.background.get_width() >> 1
            if not pos_y:
                pos_y = self.background.get_height() >> 1
            font = pygame.font.Font(None, font_size)
            text = font.render(msg, 1, rgb_color)
            text_pos = text.get_rect(centerx=pos_x, centery=pos_y)
            self.screen.blit(text, text_pos)

    def draw_walls_floors_to_screen(self):
        """
        Draws the walls and the floor if it is some X distance from the player.
        Uses PyGame's circle collision to detect what wall/floor to light up.
        """
        self.camera.update(self.player)
        # clear the background
        self.screen.blit(self.background, (0, 0))
        # shifts all objects and creates camera motion-effect (also, performance booster)
        cam_x1 = -1 * self.camera.state.x >> 5
        cam_y1 = -1 * self.camera.state.y >> 5
        cam_x2 = (-1 * self.camera.state.x + self.window_width + 32) >> 5
        cam_y2 = (-1 * self.camera.state.y + self.window_height + 32) >> 5
        for x in range(cam_x1, cam_x2):
            for y in range(cam_y1, cam_y2):
                sprite = self.map.landscape[y][x]
                if pygame.sprite.collide_circle(sprite, self.player):
                    near_viewable = True and not sprite.block_sight
                else:
                    near_viewable = False
                if near_viewable or sprite.visited:  # light sprites nearby and shadow visited sprites
                    if not sprite.block_sight:
                        sprite.visited = True
                        if near_viewable:
                            self.screen.blit(sprite.image, self.camera.apply(sprite))
                        else:
                            self.screen.blit(sprite.drk_image, self.camera.apply(sprite))

    def draw_objects_to_screen(self):
        """
        Draws all map-objects: keys, stairs, and other (objects).
        """
        for object_groups in self.map.map_objects:
            for sprite in self.map.map_objects[object_groups]:
                if pygame.sprite.collide_circle(sprite, self.player):
                    near_viewable = True and not sprite.block_sight
                else:
                    near_viewable = False
                if near_viewable or sprite.visited:  # light sprites nearby and shadow visited sprites
                    if not sprite.block_sight:
                        sprite.visited = True
                        if near_viewable:
                            self.screen.blit(sprite.image, self.camera.apply(sprite))
                        else:
                            self.screen.blit(sprite.drk_image, self.camera.apply(sprite))

    def view(self):
        """
        Handles all of the display functionality.
        """
        self.draw_walls_floors_to_screen()
        self.draw_objects_to_screen()
        self.keys_remaining_msg()
        # draw player
        for sprite in self.player_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # present changes to window
        pygame.display.flip()

    def keys_remaining_msg(self):
        """
        Displays a message, indicating how many keys remain to be collected
        """
        remaining_keys = len(self.map.map_objects["keys"])
        pos_y = self.background.get_height() - 30
        if remaining_keys > 0:
            if remaining_keys == 1:
                msg = "Collect the last key"
            else:
                msg = "Collect %s Keys" % remaining_keys
            self.display_text_to_screen(36, msg, pos_y=pos_y)
        else:
            self.display_text_to_screen(36, "Climb the stairs!", rgb_color=(255, 0, 0), pos_y=pos_y)

    def main_loop(self):
        """
        This initializes everything and starts the main-loop.
        """
        # allows key-strokes to repeat if they're held down
        pygame.key.set_repeat(500, 30)
        # clear the background: black
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        while 1:
            self.clock.tick(60)  # displays 60 max-fps
            self.controller()
            self.view()


if __name__ == "__main__":
    dun_gen = DunGen()
    dun_gen.main_loop()