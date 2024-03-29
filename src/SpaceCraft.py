import math
import os
import pygame
from .SpaceCraftBullet import SpaceCraftBullet


class SpaceCraftSprite(pygame.sprite.Sprite):
    CLIP_VERTICAL_OFFSET = 3

    def __init__(self, main_dir: str, file_name: str):
        super().__init__()
        self._position = {'x': 0, 'y': 0}
        self._rotation = 0
        img = pygame.image.load(os.path.join(main_dir, 'assets', file_name))
        img.set_colorkey((0, 0, 0))
        self.original_image = img.convert()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        # collision rectangle is 3 pixels from top (gun + 1) and 1 pixel from bottom
        # todo: rotate collision rectangle or replace with circle (preferred)
        self._collision_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height - 4)

    @property
    def position(self) -> dict[str, float]:
        return self._position

    @position.setter
    def position(self, value: dict[str, float]):
        self._position = value
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']
        self._collision_rect.centerx = self._position['x']
        self._collision_rect.centery = self._position['y'] + SpaceCraftSprite.CLIP_VERTICAL_OFFSET

    @property
    def rotation(self) -> float:
        return self._rotation

    @rotation.setter
    def rotation(self, value: float):
        self._rotation = value
        self.image = pygame.transform.rotate(self.original_image, -self._rotation)
        self.rect = self.image.get_rect()
        self.rect.centerx = self._position['x']
        self.rect.centery = self._position['y']

    @property
    def collision_rect(self) -> pygame.Rect:
        return self._collision_rect


class SpaceCraft:
    ACCELERATION = 0.250  # pixels/ms2 = 250 pixels/s2
    ROTATION_RATE = 0.180  # degrees/ms = 180 degrees/s
    AUTOMATIC_FIRE_PERIOD = 0.500  # ms => 2 bullets/s
    AUTOMATIC_FIRE_THRESHOLD = 1000  # ms = 1s

    def __init__(self, main_dir: str, display_surface: pygame.Surface, display_rect: pygame.Rect,
                 draw_group: pygame.sprite.Group, update_group: pygame.sprite.Group):
        self._keys_pressed = {
            'up': False,
            'down': False,
            'left': False,
            'right': False
        }
        # note: velocity component axis are +ve up and right.  Surface axis is +ve down and right
        self._velocity = {'horizontal': 0, 'vertical': 0}  # pixels/ms
        self._rotation = 0  # degrees clockwise from vertical up, +/-180
        self._wrapped = False
        self._automatic_fire_mode = False
        self._automatic_fire_start_time = 0
        self._automatic_fire_prev_fire_time = 0
        self._bullets = []

        self._display_surface = display_surface
        self._display_rect = display_rect
        self._main_sprite = SpaceCraftSprite(main_dir, 'spacecraft.png')
        self._wrapped_sprite = SpaceCraftSprite(main_dir, 'spacecraft.png')
        self._main_sprite.position = {'x': self._display_rect.width / 2, 'y': self._display_rect.height / 2}
        self._draw_group = draw_group
        self._update_group = update_group
        self._main_sprite.add(draw_group)

    @property
    def collision_rects(self) -> list[pygame.Rect]:
        if self._wrapped:
            return [
                self._main_sprite.collision_rect.clip(self._display_rect),
                self._wrapped_sprite.collision_rect.clip(self._display_rect)
            ]
        return [self._main_sprite.collision_rect]

    @property
    def bullets(self) -> list[SpaceCraftBullet]:
        return self._bullets

    # todo: abstract out keystrokes to an InputController (KeyHandler) and a CommandController (SpaceCraftCommand)
    # KeyHandler will direct keystrokes to the appropriate CommandController
    # SpaceCraftCommand will take those keystrokes and call accelerate/rotate/etc on the SpaceCraft
    def update(self, delta_time: int, key_events: list[pygame.event.Event]):
        self._process_keys(key_events)
        self._update_rotation(delta_time)
        self._update_velocity(delta_time)
        self._update_position(delta_time)
        self._check_wrapped()
        self._fire_gun()

    def _process_keys(self, key_events: list[pygame.event.Event]):
        key_inputs = pygame.key.get_pressed()
        if not self._keys_pressed['up'] and not self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP] and not key_inputs[pygame.K_DOWN]
            self._keys_pressed['down'] = not key_inputs[pygame.K_UP] and key_inputs[pygame.K_DOWN]
            # when both opposing keys pressed without a prior then no action will be taken

        # a previously pressed key that is still depressed takes priority over its opposite.
        elif self._keys_pressed['up'] and not self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP]
            self._keys_pressed['down'] = not key_inputs[pygame.K_UP] and key_inputs[pygame.K_DOWN]

        elif not self._keys_pressed['up'] and self._keys_pressed['down']:
            self._keys_pressed['up'] = key_inputs[pygame.K_UP] and not key_inputs[pygame.K_DOWN]
            self._keys_pressed['down'] = key_inputs[pygame.K_DOWN]

        if not self._keys_pressed['left'] and not self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT] and not key_inputs[pygame.K_RIGHT]
            self._keys_pressed['right'] = not key_inputs[pygame.K_LEFT] and key_inputs[pygame.K_RIGHT]
            # when both opposing keys pressed without a prior then no action will be taken

        # a previously pressed key that is still depressed takes priority over its opposite.
        elif self._keys_pressed['left'] and not self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT]
            self._keys_pressed['right'] = not key_inputs[pygame.K_LEFT] and key_inputs[pygame.K_RIGHT]

        elif not self._keys_pressed['left'] and self._keys_pressed['right']:
            self._keys_pressed['left'] = key_inputs[pygame.K_LEFT] and not key_inputs[pygame.K_RIGHT]
            self._keys_pressed['right'] = key_inputs[pygame.K_RIGHT]

        # basic fire control is tap key for manual fire, hold key for automatic fire
        self._keys_pressed['fire'] = False
        for event in key_events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                self._keys_pressed['fire'] = True  # manual fire based on key press
                self._automatic_fire_start_time = pygame.time.get_ticks()  # automatic fire based on time
            elif event.type == pygame.KEYUP and event.key == pygame.K_x:
                self._automatic_fire_start_time = 0

        self._automatic_fire_mode = False
        if (self._automatic_fire_start_time > 0
                and (pygame.time.get_ticks() - self._automatic_fire_start_time) > SpaceCraft.AUTOMATIC_FIRE_THRESHOLD):
            self._automatic_fire_mode = True

    def _update_rotation(self, delta_time: int):
        rotated = False
        # assume cannot rotate more than 180d in one cycle
        if self._keys_pressed['left']:
            self._rotation += -SpaceCraft.ROTATION_RATE * delta_time
            if self._rotation < -180:
                self._rotation = 180 + (self._rotation + 180)
            rotated = True

        if self._keys_pressed['right']:
            self._rotation += SpaceCraft.ROTATION_RATE * delta_time
            if self._rotation > 180:
                self._rotation = -180 + (self._rotation - 180)
            rotated = True

        if rotated:
            self._main_sprite.rotation = self._rotation

    def _update_velocity(self, delta_time: int):
        if self._keys_pressed['up']:
            self._velocity['vertical'] += SpaceCraft.ACCELERATION * delta_time * math.cos(math.radians(self._rotation))
            self._velocity['horizontal'] += SpaceCraft.ACCELERATION * delta_time * math.sin(
                math.radians(self._rotation))

        if self._keys_pressed['down']:
            self._velocity['vertical'] -= SpaceCraft.ACCELERATION * delta_time * math.cos(math.radians(self._rotation))
            self._velocity['horizontal'] -= SpaceCraft.ACCELERATION * delta_time * math.sin(
                math.radians(self._rotation))
        # todo: if speed exceeds (4 * screen height) pixels/s then show warning that approaching 80% speed of light,
        # relativistic effects weakening structural integrity, failure imminent.
        # When speed = (5 * screen height) pixels/s then spacecraft implodes

    def _update_position(self, delta_time: int):
        # drawing issues if not copied
        new_position = self._main_sprite.position.copy()
        new_position['x'] += self._velocity['horizontal'] * (delta_time / 1000)
        # vertical screen axis is +ve downwards => -ve displacement
        new_position['y'] += -self._velocity['vertical'] * (delta_time / 1000)
        self._main_sprite.position = new_position

    def _check_wrapped(self):
        self._wrapped = False
        display_width = self._display_rect.width
        display_height = self._display_rect.height

        if (self._main_sprite.rect.left < 0
                or self._main_sprite.rect.right > display_width
                or self._main_sprite.rect.top < 0
                or self._main_sprite.rect.bottom > display_height):
            self._wrapped = True
            self._wrapped_sprite.rotation = self._rotation

            # drawing issues if not copied
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
                self._wrapped_sprite.add(self._draw_group)
        else:
            self._wrapped_sprite.kill()

    def _fire_gun(self):
        if self._keys_pressed['fire'] and not self._automatic_fire_mode:
            self._create_bullet()

        # if (self._automatic_fire_mode and
        #         (pygame.time.get_ticks() - self._automatic_fire_prev_fire_time) > SpaceCraft.AUTOMATIC_FIRE_PERIOD):
        #     self._create_bullet()
        #     self._automatic_fire_prev_fire_time = pygame.time.get_ticks()

    def _create_bullet(self):
        # get bullet position.
        # determine which sprite has its gun point on screen.
        # get gun point from main sprite. check if it collides with the screen rectangle.
        # if it doesn't then the wrapped sprite must have its gun point in the screen
        firing_sprite = self._main_sprite
        gun_point = self._get_gun_point(self._main_sprite)
        if not self._display_rect.collidepoint(gun_point['x'], gun_point['y']):
            firing_sprite = self._wrapped_sprite
        # recalculate the starting center point of the bullet as an extension of the sprite
        bullet_center = self._get_gun_point(firing_sprite, SpaceCraftBullet.DIAMETER)

        bullet = SpaceCraftBullet(bullet_center, self._velocity.copy(), self._rotation)
        self._bullets.append(bullet)
        bullet.add(self._draw_group, self._update_group)

    def _get_gun_point(self, sprite: SpaceCraftSprite, offset: int = 0) -> dict[str, float]:
        # the gun point is the top center of the sprite when in its original position.
        # calculate its rotated position
        gun_center_displacement = (sprite.original_image.get_rect().height + offset) / 2
        gun_point = {
            'x': sprite.position['x'] + (gun_center_displacement * math.sin(math.radians(self._rotation))),
            'y': sprite.position['y'] - (gun_center_displacement * math.cos(math.radians(self._rotation)))
        }
        return gun_point
