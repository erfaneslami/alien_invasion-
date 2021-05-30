import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, ai_game,):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.setting = ai_game.settings
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load("img//ship.bmp")
        self.rect = self.image.get_rect()

        #  Store a decimal value for the ship's horizontal position.
        self.x = float(self.rect.x)
        # movement flags
        self.moving_right = False
        self.moving_left = False
        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.setting.ship_speed
        elif self.moving_left and self.rect.left > 0:
            self.x -= self.setting.ship_speed

        self.rect.x = self.x

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
