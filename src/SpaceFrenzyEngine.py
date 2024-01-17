import pygame

from .AsteroidGenerator import AsteroidGenerator
from .CollisionManager import CollisionManager
from .Hud import Hud
from .SpaceCraft import SpaceCraft
from .HudData import HudData


class SpaceFrenzyEngine:
    SCREEN_WIDTH = 800
    SPACE_HEIGHT = 600
    HUD_HEIGHT = 35

    def __init__(self, main_dir: str):
        self.main_dir = main_dir
        self._display_surface = None
        self._background = None
        self._draw_group = None
        self._update_group = None
        self._space_rect = None
        self._hud_rect = None
        self._asteroid_generator = None

    def start(self):
        pygame.init()

        # cannot subsurface the display surface when HW accelerated, so to be safe use bounding Rects
        screen_rect = pygame.Rect(0, 0, SpaceFrenzyEngine.SCREEN_WIDTH,
                                  SpaceFrenzyEngine.SPACE_HEIGHT + SpaceFrenzyEngine.HUD_HEIGHT)
        self._space_rect = pygame.Rect(0, 0, SpaceFrenzyEngine.SCREEN_WIDTH, SpaceFrenzyEngine.SPACE_HEIGHT)
        self._hud_rect = pygame.Rect(0, SpaceFrenzyEngine.SPACE_HEIGHT, SpaceFrenzyEngine.SCREEN_WIDTH,
                                     SpaceFrenzyEngine.HUD_HEIGHT)
        surface_flags = pygame.SCALED
        self._display_surface = pygame.display.set_mode(size=screen_rect.size, flags=surface_flags)
        self._background = pygame.Surface(screen_rect.size)
        self._background.fill((0, 0, 0))
        self._update_group = pygame.sprite.Group()
        # draw_group = pygame.sprite.RenderClear()
        self._draw_group = pygame.sprite.OrderedUpdates()

        while self._restart_game():
            pass
        pygame.quit()

    def _restart_game(self) -> bool:
        # todo: make sure all object references are cleared i.e. empty lists inside objects.  is this required?
        self._update_group.empty()
        self._draw_group.empty()
        space_craft = SpaceCraft(self.main_dir, self._display_surface, self._space_rect,
                                 self._draw_group, self._update_group)
        self._asteroid_generator = AsteroidGenerator(self._display_surface, self._space_rect, self._draw_group,
                                                     self._update_group)
        collision_manager = CollisionManager(space_craft, self._asteroid_generator, self._space_rect)

        if not self._wait_on_keyup(pygame.K_SPACE, 'Arrow keys to move, X to fire.  Press SPACE to start'):
            return False

        clock = pygame.time.Clock()
        quit_game = False
        running = True
        while running:
            dt = clock.tick(60)
            space_craft.update(dt, pygame.event.get(eventtype=[pygame.KEYUP, pygame.KEYDOWN], pump=False))
            self._asteroid_generator.update()
            self._update_group.update(dt)
            collision_manager.update()
            hud_data = HudData(
                self._asteroid_generator.level,
                self._asteroid_generator.asteroid_level_count,
                self._asteroid_generator.asteroids_destroyed_level_count,
                self._asteroid_generator.asteroids_destroyed_total_count,
                self._asteroid_generator.time_to_next_generation,
                'Arrow keys to move, X to fire'
            )
            # add the hud to the draw group last so that it draws over any out-of-space_rect objects
            Hud(self._hud_rect, self._draw_group, hud_data)
            self._draw()
            quit_game = len(pygame.event.get(eventtype=pygame.QUIT)) > 0
            running = not quit_game and not collision_manager.game_over

        if collision_manager.game_over:
            quit_game = not self._wait_on_keyup(pygame.K_SPACE, 'GAME OVER!  Press SPACE to reset')

        return not quit_game

    def _wait_on_keyup(self, key: int, message: str) -> bool:
        hud_data = HudData(
            self._asteroid_generator.level,
            self._asteroid_generator.asteroid_level_count,
            self._asteroid_generator.asteroids_destroyed_level_count,
            self._asteroid_generator.asteroids_destroyed_total_count,
            self._asteroid_generator.time_to_next_generation,
            message
        )
        Hud(self._hud_rect, self._draw_group, hud_data)
        self._draw()
        quit_game = False
        can_continue = False
        while not (can_continue or quit_game):
            for event in pygame.event.get(eventtype=[pygame.KEYUP], pump=False):
                if event.key == key:
                    can_continue = True
            if len(pygame.event.get(eventtype=pygame.QUIT)) > 0:
                quit_game = True

        return not quit_game

    def _draw(self):
        dirty_rects = self._draw_group.draw(self._display_surface)
        pygame.display.update(dirty_rects)
        self._draw_group.clear(self._display_surface, self._background)
