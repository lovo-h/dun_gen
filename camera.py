"""
Author: Hector Lovo
Created on: 5/3/2015

This dungeon generator was created as a demo for WillowTreeApps.
"""
from pygame import Rect


class Camera(object):
    """
    Camera that follows the player around.
    """

    def __init__(self, camera_func, map_width, map_height, win_width, win_height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, map_width, map_height)
        self.win_width = win_width
        self.win_height = win_height

    def apply(self, target):
        """
        Offsets the target some distance to represent motion.
        :param target: (Rect) to move.
        :return: (Rect) target in its new position.
        """
        return target.rect.move(self.state.topleft)

    def update(self, target):
        """
        This invokes the complex_camera function and finalizes the camera motion.
        """
        self.state = self.camera_func(self.state, target.rect, self.win_width, self.win_height)


def complex_camera(camera, target_rect, win_width, win_height):
    """
    Allows the camera to scroll everywhere, except at the vertices of the map.
    :param camera: (camera) the camera itself
    :param target_rect: (Rect) target rectangle
    :param win_width: (int)  window width
    :param win_height: (int) window height
    :return: (Rect) with new coordinates and dimensions
    """
    half_width = win_width >> 1
    half_height = win_height >> 1
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + half_width, -t + half_height, w, h  # center the player
    l = min(0, l)  # stops camera from scrolling at the left edge
    l = max(-(camera.width - win_width), l)  # stops camera from scrolling at the right edge
    t = max(-(camera.height - win_height), t)  # stops camera from scrolling at the bottom
    t = min(0, t)  # stops camera from scrolling at the top
    return Rect(l, t, w, h)