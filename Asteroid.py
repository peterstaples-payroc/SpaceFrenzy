import math  # todo: is it better to import only the objects needed, rather than the whole package?

import pygame
from Projectile import Projectile


class Asteroid(Projectile):
    def __init__(self, position: dict[str, int], velocity: dict[str, float], direction: float, diameter: int,
                 containing_rect: pygame.Rect):
        super().__init__(position, velocity, direction)
        self._active = False  # flags that the asteroid is not fully on screen yet
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
        self.rect = self.image.get_rect()
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']

    @property
    def active(self):
        return self._active

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


class AsteroidPrimary(Asteroid):
    def __init__(self, position: dict[str, int], velocity: dict[str, float], direction: float, diameter: int,
                 containing_rect: pygame.Rect):
        super().__init__(position, velocity, direction, diameter, containing_rect)
        self._fragments = []

    @property
    def fragments(self):
        return self._fragments


class AsteroidFragment(Asteroid):
    def __init__(self, position: dict[str, int], velocity: dict[str, float], direction: float, diameter: int,
                 containing_rect: pygame.Rect, primary_asteroid: AsteroidPrimary):
        super().__init__(position, velocity, direction, diameter, containing_rect)
        self.primary_asteroid = primary_asteroid
