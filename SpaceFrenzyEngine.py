import pygame
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
        # update_group = pygame.sprite.Group()
        draw_group = pygame.sprite.RenderClear()
        space_craft = SpaceCraft(self.main_dir,
                                 SpaceFrenzyEngine.SCREEN_WIDTH / 2,
                                 SpaceFrenzyEngine.SCREEN_HEIGHT / 2,
                                 draw_group)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            dt = clock.tick(60)
            draw_group.clear(display_surface, background)
            # update_group.update(dt)
            space_craft.update(dt)
            dirty_rects = draw_group.draw(display_surface)
            pygame.display.update(dirty_rects)

        pygame.quit()
