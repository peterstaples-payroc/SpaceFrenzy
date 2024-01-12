import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, velocity, direction):
        super().__init__()
        self._position = position
        self._velocity = velocity
        self._direction = direction
        self.rect = pygame.Rect(0, 0, 0, 0)  # dummy Rect.  Must be overridden

    @property
    def position(self):
        return self._position

    def update(self, delta_time):
        self._position['x'] += self._velocity['horizontal'] * (delta_time / 1000)
        self._position['y'] += -self._velocity['vertical'] * (delta_time / 1000)
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']
