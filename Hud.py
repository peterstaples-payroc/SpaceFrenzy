import pygame

from HudData import HudData


class Hud(pygame.sprite.Sprite):
    BACKGROUND_COLOUR = (185, 185, 185)
    TEXT_COLOUR = (0, 0, 0)

    def __init__(self, display_rect: pygame.Rect, draw_group: pygame.sprite.Group, data: HudData):
        super().__init__()
        self.image = pygame.Surface((display_rect.width, display_rect.height))
        self.rect = display_rect
        self.image.fill(Hud.BACKGROUND_COLOUR)
        draw_group.add(self)

        self._font = pygame.font.Font(None, 24)
        text = f'Level: {data.level}'
        self.image.blit(self._font.render(text, True, Hud.TEXT_COLOUR, Hud.BACKGROUND_COLOUR),
                        (10, 10))
        text = f'Asteroids: {data.asteroids_generated_in_level} / {data.asteroids_destroyed_in_level} / {data.asteroids_destroyed_total}'
        self.image.blit(self._font.render(text, True, Hud.TEXT_COLOUR, Hud.BACKGROUND_COLOUR),
                        (150, 10))
        self.image.blit(self._font.render(data.message, True, Hud.TEXT_COLOUR, Hud.BACKGROUND_COLOUR),
                        (350, 10))

