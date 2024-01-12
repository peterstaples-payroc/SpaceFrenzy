import pygame

from AsteroidGenerator import AsteroidGenerator
from CollisionManager import CollisionManager
from SpaceCraft import SpaceCraft


class SpaceFrenzyEngine:
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 640
    SCREEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def __init__(self, main_dir):
        self.main_dir = main_dir

    def start(self):
        pygame.init()
        surface_flags = pygame.SCALED
        display_surface = pygame.display.set_mode(size=SpaceFrenzyEngine.SCREEN_RECT.size, flags=surface_flags)
        clock = pygame.time.Clock()
        running = True

        # init objects
        background = pygame.Surface(SpaceFrenzyEngine.SCREEN_RECT.size)
        background.fill((0, 0, 0))
        update_group = pygame.sprite.Group()
        draw_group = pygame.sprite.RenderClear()
        space_craft = SpaceCraft(self.main_dir,
                                 SpaceFrenzyEngine.SCREEN_WIDTH / 2,
                                 SpaceFrenzyEngine.SCREEN_HEIGHT / 2,
                                 draw_group, update_group)
        asteroid_generator = AsteroidGenerator(draw_group, update_group)
        collision_manager = CollisionManager(space_craft, asteroid_generator)

        while running:
            dt = clock.tick(60)
            draw_group.clear(display_surface, background)
            space_craft.update(dt, pygame.event.get(eventtype=[pygame.KEYUP, pygame.KEYDOWN], pump=False))
            asteroid_generator.update()
            update_group.update(dt)
            collision_manager.update()
            dirty_rects = draw_group.draw(display_surface)
            pygame.display.update(dirty_rects)
            running = (len(pygame.event.get(eventtype=pygame.QUIT, pump=True)) == 0
                       and not collision_manager.game_over)

        if collision_manager.game_over:
            print('GAME OVER!')
        pygame.quit()
