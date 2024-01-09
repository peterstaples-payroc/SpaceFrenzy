import math
import os
import pygame


class SpaceCraftSprite(pygame.sprite.Sprite):
    def __init__(self, main_dir, file_name):
        super().__init__()
        self._position = {'x': 0, 'y': 0}
        self._rotation = 0
        img = pygame.image.load(os.path.join(main_dir, 'assets', file_name))
        img.set_colorkey((0, 0, 0))
        self.original_image = img.convert()
        self.image = self.original_image
        self.rect = self.image.get_rect()

    @property
    def position(self) -> dict[str, int]:
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self._set_top_left()

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.image = pygame.transform.rotate(self.original_image, -self._rotation)
        self.rect = self.image.get_rect()
        self._set_top_left()

    def _set_top_left(self):
        self.rect.left = self._position['x'] - (self.rect.width / 2)
        self.rect.top = self._position['y'] - (self.rect.height / 2)


class SpaceCraft:
    def __init__(self, main_dir, x_pos_center, y_pos_center, *groups: pygame.sprite.Group):
        self._keys_pressed = {
            'up': False,
            'down': False,
            'left': False,
            'right': False
        }
        self._speed = {'horizontal': 0, 'vertical': 0}  # pixels/s
        self._acceleration = 0.250  # pixels/ms2 = 250 pixels/s2
        self._rotation = 0  # degrees clockwise from vertical up, +/-180
        self._rotation_rate = 0.180  # degrees/ms = 180 degrees/s
        self._wrapped = False

        self._main_sprite = SpaceCraftSprite(main_dir, 'spacecraft.png')
        self._wrapped_sprite = SpaceCraftSprite(main_dir, 'spacecraft.png')
        self._main_sprite.position = {'x': x_pos_center, 'y': y_pos_center}
        self._groups = groups
        self._main_sprite.add(groups)
        self._display_surface = pygame.display.get_surface()

    # todo: abstract out keystrokes to an InputController (KeyHandler) and a CommandController (SpaceCraftCommand)
    # KeyHandler will direct keystrokes to the appropriate CommandController
    # SpaceCraftCommand will take those keystrokes and call accelerate/rotate/etc on the SpaceCraft
    def update(self, ms_in_cycle):
        self._process_keys()
        self._update_rotation(ms_in_cycle)
        self._update_speed(ms_in_cycle)
        self._update_position(ms_in_cycle)
        self._check_wrapped()

    def _process_keys(self):
        key_inputs = pygame.key.get_pressed()
        if not self._keys_pressed['up'] and not self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP] and not key_inputs[pygame.K_DOWN]
            self._keys_pressed['down'] = not key_inputs[pygame.K_UP] and key_inputs[pygame.K_DOWN]
            # when both opposing keys pressed without a prior then no action will be taken

        # a previously pressed key that is still depressed takes priority over its opposite.
        if self._keys_pressed['up'] and not self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP]
            self._keys_pressed['down'] = not key_inputs[pygame.K_UP] and key_inputs[pygame.K_DOWN]

        if not self._keys_pressed['up'] and self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP] and not key_inputs[pygame.K_DOWN]
            self._keys_pressed['down'] = key_inputs[pygame.K_DOWN]

        if not self._keys_pressed['left'] and not self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT] and not key_inputs[pygame.K_RIGHT]
            self._keys_pressed['right'] = not key_inputs[pygame.K_LEFT] and key_inputs[pygame.K_RIGHT]
            # when both opposing keys pressed without a prior then no action will be taken

        # a previously pressed key that is still depressed takes priority over its opposite.
        if self._keys_pressed['left'] and not self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT]
            self._keys_pressed['right'] = not key_inputs[pygame.K_LEFT] and key_inputs[pygame.K_RIGHT]

        if not self._keys_pressed['left'] and self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT] and not key_inputs[pygame.K_RIGHT]
            self._keys_pressed['right'] = key_inputs[pygame.K_RIGHT]

    def _update_rotation(self, ms_in_cycle):
        rotated = False
        # assume cannot rotate more than 180d in one cycle
        if self._keys_pressed['left']:
            self._rotation += -self._rotation_rate * ms_in_cycle
            if self._rotation < -180:
                self._rotation = 180 + (self._rotation + 180)
            rotated = True

        if self._keys_pressed['right']:
            self._rotation += self._rotation_rate * ms_in_cycle
            if self._rotation > 180:
                self._rotation = -180 + (self._rotation - 180)
            rotated = True

        if rotated:
            self._main_sprite.rotation = self._rotation

    def _update_speed(self, ms_in_cycle):
        if self._keys_pressed['up']:
            self._speed['vertical'] += self._acceleration * ms_in_cycle * math.cos(math.radians(self._rotation))
            self._speed['horizontal'] += self._acceleration * ms_in_cycle * math.sin(math.radians(self._rotation))

        if self._keys_pressed['down']:
            self._speed['vertical'] -= self._acceleration * ms_in_cycle * math.cos(math.radians(self._rotation))
            self._speed['horizontal'] -= self._acceleration * ms_in_cycle * math.sin(math.radians(self._rotation))
        # todo: if speed exceeds (4 * screen height) pixels/s then show warning that approaching 80% speed of light,
        # relativistic effects weakening structural integrity, failure imminent.
        # When speed = (5 * screen height) pixels/s then spacecraft implodes

    def _update_position(self, ms_in_cycle):
        dx = self._speed['horizontal'] * (ms_in_cycle / 1000)
        # vertical screen axis is +ve downwards => -ve displacement
        dy = -self._speed['vertical'] * (ms_in_cycle / 1000)
        new_position = self._main_sprite.position.copy()
        new_position['x'] += dx
        new_position['y'] += dy
        self._main_sprite.position = new_position

    def _check_wrapped(self):
        self._wrapped = False
        display_width = self._display_surface.get_width()
        display_height = self._display_surface.get_height()

        if (self._main_sprite.rect.left < 0
                or self._main_sprite.rect.right > display_width
                or self._main_sprite.rect.top < 0
                or self._main_sprite.rect.bottom > display_height):
            self._wrapped = True
            self._wrapped_sprite.rotation = self._rotation

            wrapped_sprite_position = self._main_sprite.position.copy()

            if self._main_sprite.rect.left < 0:
                wrapped_sprite_position['x'] += display_width
            elif self._main_sprite.rect.right > display_width:
                wrapped_sprite_position['x'] -= display_width

            if self._main_sprite.rect.top < 0:
                wrapped_sprite_position['y'] += display_height
            elif self._main_sprite.rect.bottom > display_height:
                wrapped_sprite_position['y'] -= display_height

            self._wrapped_sprite.position = wrapped_sprite_position

            # if the wrapped sprite is fully on screen then swap the main sprite in its place
            # else show it
            if (self._wrapped_sprite.rect.left >= 0
                    and self._wrapped_sprite.rect.right <= display_width
                    and self._wrapped_sprite.rect.top >= 0
                    and self._wrapped_sprite.rect.bottom <= display_height):
                self._main_sprite.position = wrapped_sprite_position
                self._wrapped_sprite.kill()
            else:
                self._wrapped_sprite.add(self._groups)
        else:
            self._wrapped_sprite.kill()
