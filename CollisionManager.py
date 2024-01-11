import pygame

from Asteroid import Asteroid
from AsteroidGenerator import AsteroidGenerator
from SpaceCraft import SpaceCraft
from SpaceCraftBullet import SpaceCraftBullet


class CollisionManager:
    def __init__(self, space_craft: SpaceCraft, asteroid_generator: AsteroidGenerator):
        self._space_craft = space_craft
        self._asteroid_generator = asteroid_generator
        self._display_rect = pygame.display.get_surface().get_rect()

    def update(self):
        for bullet in self._space_craft.bullets.copy():
            # bullet-edge collisions
            if not self._display_rect.colliderect(bullet.rect):
                self._space_craft.bullets.remove(bullet)
                bullet.kill()
            # bullet-spacecraft collisions
            # asteroid-bullet collisions
            for asteroid in self._asteroid_generator.asteroids.copy():
                self._check_asteroid_bullet_collision(asteroid, bullet)

        # asteroid-spacecraft collisions

    def _check_asteroid_bullet_collision(self, asteroid: Asteroid, bullet: SpaceCraftBullet):
        if not asteroid.active:
            return
        # check if center point of circle is within the radius distance of the closest point on the rectangle
        closest_x = pygame.math.clamp(asteroid.rect.centerx, bullet.rect.left, bullet.rect.right)
        closest_y = pygame.math.clamp(asteroid.rect.centery, bullet.rect.top, bullet.rect.bottom)
        distance_x = asteroid.rect.centerx - closest_x
        distance_y = asteroid.rect.centery - closest_y
        if (distance_x ** 2) + (distance_y ** 2) <= (asteroid.radius ** 2):
            self._asteroid_generator.asteroids.remove(asteroid)
            asteroid.kill()
            self._space_craft.bullets.remove(bullet)
            bullet.kill()
