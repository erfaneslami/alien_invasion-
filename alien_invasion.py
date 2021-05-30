import sys
from time import sleep
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        # Create an instance to store game statistics
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        # self.game_active = True
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        # make play button
        self.play_button = Button(self, "play")
        pygame.display.set_caption("Alien Invasion")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # set back ground color in every draw of screen/surface
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullets in self.bullets.sprites():
            bullets.draw_bullet()
        # Make the most recently drawn screen visible.
        self.aliens.draw(self.screen)
        # Draw the score information.
        self.sb.show_score()
        #  Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _check_events(self):
        """ Respond to keypresses and mouse events."""
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                sys.exit()
            elif events.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

            # moving left and right events
            elif events.type == pygame.KEYDOWN:
                self._check_keydown_events(events)

            elif events.type == pygame.KEYUP:
                self._check_keyup_events(events)

    def _check_keydown_events(self, events):
        """Respond to keypresses."""
        if events.key == pygame.K_RIGHT:
            # Move the ship to the right.
            self.ship.moving_right = True
        elif events.key == pygame.K_LEFT:
            # Move the ship to the left.
            self.ship.moving_left = True
        elif events.key == pygame.K_SPACE:
            self._fire_bullet()

        elif events.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, events):
        """Respond to key releases."""
        if events.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif events.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:  # lay button o az bayn mibare  bad az click
            self.stats.game_active = True

            # rest game setting
            self.settings.initialize_dynamic_settings()
            # reset the game elements
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ship()
            self.aliens.empty()
            self.bullets.empty()

            # hide a mouse  cursor
            pygame.mouse.set_visible(False)

            self._create_fleet()
            self.ship.center_ship()

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        # get rid of bulltets of out screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions :
            for aliens in collisions.values(): # agar tir ra bozorg konim va be chand alien ba ham barkhod konad
                # emtiaze hamaro be ma midahad
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()  # use this to re drow the image and pass to the rendering
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.sb.increase_level()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        self.aliens.add(alien)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        alien.rect.x = alien.x
        self.aliens.add(alien)

    def _update_aliens(self):
        """
         Check if the fleet is at an edge,
         then update the positions of all aliens in the fleet.
         """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

            # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ship_left > 0:
            self.stats.ship_left -= 1
            self.sb.prep_ship()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
