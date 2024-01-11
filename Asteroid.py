import pygame
from pygame import Vector2

from Projectile import Projectile


class Asteroid(Projectile):
    def __init__(self, position, velocity, direction, diameter, containing_rect: pygame.Rect):
        super().__init__(position, velocity, direction)
        self._active = False  # flags that the asteroid is not fully on screen yet
        self._diameter = diameter
        self._containing_rect = containing_rect
        surface = pygame.Surface((self._diameter, self._diameter))
        surface.set_colorkey((0, 0, 0))
        radius = diameter / 2
        pygame.draw.circle(surface, (0, 255, 0), (radius, radius), radius)
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']

    def update(self, delta_time):
        super().update(delta_time)
        # no collision detection on first activation as the trailing edge of the asteroid
        # collides with the edge of the screen causing it to reflect
        if self._containing_rect.contains(self.rect):
            self._active = True
        elif self._active:
            top_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.top, self._containing_rect.width,
                                   1)
            right_edge = pygame.Rect(self._containing_rect.right, self._containing_rect.top, 1,
                                     self._containing_rect.height)
            bottom_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.bottom,
                                      self._containing_rect.width, 1)
            left_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.top, 1,
                                    self._containing_rect.height)
            if top_edge.colliderect(self.rect) or bottom_edge.colliderect(self.rect):
                self._velocity['vertical'] *= -1
            if left_edge.colliderect(self.rect) or right_edge.colliderect(self.rect):
                self._velocity['horizontal'] *= -1
