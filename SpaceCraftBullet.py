import math
import pygame
from Projectile import Projectile


class SpaceCraftBullet(Projectile):
    DIAMETER = 2
    SPEED = 250  # pixels/s

    def __init__(self, position, initial_velocity, direction, active_rect):
        super().__init__(position, initial_velocity, direction)
        self._active_rect = active_rect
        self._velocity['horizontal'] += SpaceCraftBullet.SPEED * math.sin(math.radians(self._direction))
        self._velocity['vertical'] += SpaceCraftBullet.SPEED * math.cos(math.radians(self._direction))
        surface = pygame.Surface((SpaceCraftBullet.DIAMETER, SpaceCraftBullet.DIAMETER))
        surface.set_colorkey((0, 0, 0))
        surface.fill([255, 0, 0])
        self.image = surface
        self.rect = self.image.get_rect()
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']

    def update(self, delta_time):
        super().update(delta_time)
        if not self._active_rect.colliderect(self.rect):
            self.kill()
