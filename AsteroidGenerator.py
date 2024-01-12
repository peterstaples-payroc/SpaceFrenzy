import math
import random
import pygame.time
from Asteroid import Asteroid


class AsteroidGenerator:
    MINIMUM_LEVEL = 1
    MAXIMUM_LEVEL = 99
    MINIMUM_GENERATION_PERIOD = 5000  # seconds
    MAXIMUM_GENERATION_PERIOD = 60000  # seconds
    MINIMUM_DIAMETER = 10  # pixels
    MAXIMUM_DIAMETER = 75  # pixels
    MINIMUM_SPEED = 150  # pixels/s
    MAXIMUM_SPEED = 250  # pixels/s
    MINIMUM_AREA = ((MINIMUM_DIAMETER / 2) ** 2) * math.pi

    def __init__(self, display_surface, display_rect, draw_group, update_group):
        self._draw_group = draw_group
        self._update_group = update_group
        self._display_surface = display_surface
        self._display_rect = display_rect

        self._level = 0  # the level of the game
        self._level_generation_period = 0  # the time between asteroid generations for the current level
        self._asteroid_level_count = self._level  # number of asteroids generated so far in this level.  Set to level to trigger new level
        self._asteroids_destroyed_level_count = 0
        self._asteroids_destroyed_total_count = 0
        self._asteroids = []  # the asteroids remaining in this level
        self._prev_generation_time = 0  # the previous time an asteroid was generated
        self._time_to_next_generation = 0
        random.seed()

    @property
    def level(self):
        return self._level

    @property
    def asteroid_level_count(self):
        return self._asteroid_level_count

    @property
    def asteroids_destroyed_level_count(self):
        return self._asteroids_destroyed_level_count

    @property
    def asteroids_destroyed_total_count(self):
        return self._asteroids_destroyed_total_count

    @property
    def time_to_next_generation(self):
        return self._time_to_next_generation

    @property
    def asteroids(self) -> list[Asteroid]:
        return self._asteroids.copy()

    def remove(self, asteroid: Asteroid) -> None:
        self._asteroids.remove(asteroid)
        if asteroid.primary:
            self._asteroids_destroyed_level_count += 1
            self._asteroids_destroyed_total_count += 1

    def fragment(self, asteroid):
        remaining_area = asteroid.area
        remaining_energy = asteroid.energy
        while remaining_area > (AsteroidGenerator.MINIMUM_AREA * 1.25):  # factor in reduction by 20%
            # generate new asteroids up to 80% of the original size
            new_area = random.randint(int(AsteroidGenerator.MINIMUM_AREA), int(asteroid.area * 0.8))
            remaining_area = remaining_area - new_area
            new_diameter = math.sqrt(new_area / math.pi) * 2  # todo: use squared values for speed?
            new_energy = random.randint(0, int(remaining_energy * 0.8))
            remaining_energy = remaining_energy - new_energy
            new_speed = math.sqrt(2 * new_energy / new_area)
            new_rotation = random.randint(-180, 180)
            new_velocity = {
                'horizontal': new_speed * math.sin(math.radians(new_rotation)),
                'vertical': new_speed * math.cos(math.radians(new_rotation))
            }
            new_position = asteroid.position.copy()

            new_asteroid = Asteroid(new_position, new_velocity, new_rotation, int(new_diameter),
                                    self._display_rect)
            self._asteroids.append(new_asteroid)
            new_asteroid.add([self._draw_group, self._update_group])

    def update(self):
        # generation rules
        # -asteroid generation period = Max period - (((max period - min period)/max level) * (level - 1))
        # => max generation period = 60 - (((60 - 5)/99) * 0 = 60s
        # => min generation period = 60 - (((60 - 5)/99) * 98 = 5.56s
        # -number of asteroids per level = level

        # level complete
        elapsed_time = pygame.time.get_ticks() - self._prev_generation_time
        self._time_to_next_generation = self._level_generation_period - elapsed_time
        if self._asteroid_level_count == self._level and len(self._asteroids) == 0:
            self._level += 1
            print('Level ', self._level)
            period_reduction = ((AsteroidGenerator.MAXIMUM_GENERATION_PERIOD - AsteroidGenerator.MINIMUM_GENERATION_PERIOD) / AsteroidGenerator.MAXIMUM_LEVEL) * (self._level - 1)
            self._level_generation_period = AsteroidGenerator.MAXIMUM_GENERATION_PERIOD - period_reduction
            self._generate()
            self._prev_generation_time = pygame.time.get_ticks()
            self._asteroid_level_count = 1
            self._asteroids_destroyed_level_count = 0
        elif ((elapsed_time > self._level_generation_period or len(self._asteroids) == 0)
              and self._asteroid_level_count < self._level):
            self._generate()
            self._prev_generation_time = pygame.time.get_ticks()
            self._asteroid_level_count += 1

    def _generate(self):
        # generation process
        # -select random diameter between min and max
        # -select random position off-screen such that the asteroid is just off the screen
        # -select random position on-screen, get calculate velocity between that point and asteroid center point
        # -create asteroid

        diameter = random.randint(AsteroidGenerator.MINIMUM_DIAMETER, AsteroidGenerator.MAXIMUM_DIAMETER)
        # top=0, right=1, bottom=2, left=3
        # could use an outer rectangle to get values, as for inner_rect
        location = random.randint(0, 3)
        if location == 0:
            position = {
                'x': random.randint(0, self._display_rect.width + (diameter * 2)) - diameter,
                'y': -(diameter / 2)
            }
        elif location == 1:
            position = {
                'x': self._display_rect.width + (diameter / 2),
                'y': random.randint(0, self._display_rect.height + (diameter * 2)) - diameter
            }
        elif location == 2:
            position = {
                'x': random.randint(0, self._display_rect.width + (diameter * 2)) - diameter,
                'y': self._display_rect.height + (diameter / 2)
            }
        else:  # location == 3
            position = {
                'x': -(diameter / 2),
                'y': random.randint(0, self._display_rect.height + (diameter * 2)) - diameter
            }
        # use inner rect such that the asteroid is guaranteed to fully appear
        inner_rect = pygame.Rect(diameter, diameter, self._display_rect.width - (diameter * 2),
                                 self._display_rect.height - (diameter * 2))
        target_point = {
            'x': random.randint(inner_rect.left, inner_rect.right),
            'y': random.randint(inner_rect.top, inner_rect.bottom)
        }
        # target_point = {
        #     'x': random.randint(diameter, self._display_surface.get_width() - diameter),
        #     'y': random.randint(diameter, self._display_surface.get_height() - diameter)
        # }
        # vector in y-axis +ve up
        targeting_vector = {
            'x': target_point['x'] - position['x'],
            'y': position['y'] - target_point['y']
        }
        magnitude = math.sqrt(targeting_vector['x'] ** 2 + targeting_vector['y'] ** 2)
        speed = random.randint(AsteroidGenerator.MINIMUM_SPEED, AsteroidGenerator.MAXIMUM_SPEED)
        if targeting_vector['x'] > 0 and targeting_vector['y'] > 0:
            targeting_rotation_rad = math.asin(targeting_vector['x'] / magnitude)
        elif targeting_vector['x'] > 0 and targeting_vector['y'] < 0:
            targeting_rotation_rad = math.acos(targeting_vector['y'] / magnitude)
        elif targeting_vector['x'] < 0 and targeting_vector['y'] > 0:
            targeting_rotation_rad = math.asin(targeting_vector['x'] / magnitude)
        else:  # targeting_vector['x'] < 0 and targeting_vector['y'] < 0
            targeting_rotation_rad = -math.acos(targeting_vector['y'] / magnitude)
        velocity = {
            'horizontal': speed * math.sin(targeting_rotation_rad),
            'vertical': speed * math.cos(targeting_rotation_rad)
        }

        asteroid = Asteroid(position, velocity, math.degrees(targeting_rotation_rad), diameter,
                            self._display_rect, True)
        self._asteroids.append(asteroid)
        asteroid.add([self._draw_group, self._update_group])
