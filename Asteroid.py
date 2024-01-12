import math  # todo: is it better to import only the objects needed, rather than the whole package?

import pygame
from Projectile import Projectile


class Asteroid(Projectile):
    MINIMUM_DIAMETER = 10  # pixels
    MAXIMUM_DIAMETER = 75  # pixels
    MINIMUM_SPEED = 50  # pixels/s
    MAXIMUM_SPEED = 250  # pixels/s
    MINIMUM_AREA = ((MINIMUM_DIAMETER / 2) ** 2) * math.pi

    def __init__(self, position: dict[str, int], velocity: dict[str, float], direction: float, diameter: int,
                 containing_rect: pygame.Rect, primary=False):
        super().__init__(position, velocity, direction)
        self._active = False  # flags that the asteroid is not fully on screen yet
        self._primary = primary
        self._radius = diameter / 2
        self._area = math.pi * (self._radius ** 2)
        self._energy = (self.area * ((self._velocity['horizontal'] ** 2) + (self._velocity['vertical'] ** 2))) / 2
        self._containing_rect = containing_rect
        self._top_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.top,
                                     self._containing_rect.width, 1)
        self._right_edge = pygame.Rect(self._containing_rect.right, self._containing_rect.top,
                                       1, self._containing_rect.height)
        self._bottom_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.bottom,
                                        self._containing_rect.width, 1)
        self._left_edge = pygame.Rect(self._containing_rect.left, self._containing_rect.top,
                                      1, self._containing_rect.height)
        surface = pygame.Surface((diameter, diameter))
        surface.set_colorkey((0, 0, 0))
        pygame.draw.circle(surface, (0, 255, 0), (self._radius, self._radius), self._radius)
        self.image = surface
        self._base_rect = self.image.get_rect()
        self.rect = self._base_rect
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']

    @property
    def active(self):
        return self._active

    @property
    def primary(self) -> bool:
        return self._primary

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def area(self) -> float:
        return self._area

    @property
    def energy(self) -> float:
        return self._energy

    def update(self, delta_time: int):
        super().update(delta_time)
        # no collision detection on first activation as the trailing edge of the asteroid
        # collides with the edge of the screen causing it to reflect
        if self._active:
            if self._top_edge.colliderect(self.rect) or self._bottom_edge.colliderect(self.rect):
                self._velocity['vertical'] *= -1
            if self._left_edge.colliderect(self.rect) or self._right_edge.colliderect(self.rect):
                self._velocity['horizontal'] *= -1
        elif self._containing_rect.contains(self.rect):
            self._active = True
        # else:
        #     self.rect = self._base_rect.clip(self._containing_rect)
        #     self.rect.centerx = self._position['x']
        #     self.rect.centery = self._position['y']
