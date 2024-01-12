import pygame

from Asteroid import Asteroid
from AsteroidGenerator import AsteroidGenerator
from SpaceCraft import SpaceCraft


class CollisionManager:
    def __init__(self, space_craft: SpaceCraft, asteroid_generator: AsteroidGenerator, display_rect: pygame.Rect):
        self._space_craft = space_craft
        self._asteroid_generator = asteroid_generator
        self._display_rect = display_rect
        self._game_over = False

    @property
    def game_over(self):
        return self._game_over

    def update(self):
        for bullet in self._space_craft.bullets.copy():
            # bullet-edge collisions
            if not self._display_rect.colliderect(bullet.rect):
                self._space_craft.bullets.remove(bullet)
                bullet.kill()
        for bullet in self._space_craft.bullets.copy():
            # asteroid-bullet collisions
            collision = False
            for asteroid in self._asteroid_generator.asteroids:
                if collision:
                    break
                if self._check_asteroid_rect_collision(asteroid, bullet.rect):
                    self._asteroid_generator.remove(asteroid)
                    asteroid.kill()
                    self._space_craft.bullets.remove(bullet)
                    bullet.kill()
                    self._asteroid_generator.fragment(asteroid)
                    collision = True
        for bullet in self._space_craft.bullets.copy():
            # bullet-spacecraft collisions
            for r in self._space_craft.collision_rects:
                if r.colliderect(bullet.rect):
                    self._game_over = True

        # asteroid-spacecraft collisions
        for asteroid in self._asteroid_generator.asteroids:
            for rect in self._space_craft.collision_rects:
                if self._check_asteroid_rect_collision(asteroid, rect):
                    self._game_over = True

    def _check_asteroid_rect_collision(self, asteroid: Asteroid, rect: pygame.Rect) -> bool:
        if not asteroid.active:
            return False
        # check if center point of circle is within the radius distance of the closest point on the rectangle
        closest_x = pygame.math.clamp(asteroid.rect.centerx, rect.left, rect.right)
        closest_y = pygame.math.clamp(asteroid.rect.centery, rect.top, rect.bottom)
        distance_x = asteroid.rect.centerx - closest_x
        distance_y = asteroid.rect.centery - closest_y
        if (distance_x ** 2) + (distance_y ** 2) <= (asteroid.radius ** 2):
            return True
        return False
