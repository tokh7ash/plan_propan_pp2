"""main.py — entry point for TSIS-3 Racer."""
import pygame
import sys
from pygame.locals import *

from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import (main_menu_screen, name_entry_screen,
                settings_screen, leaderboard_screen, game_over_screen,
                SCREEN_W, SCREEN_H, DARK)
from racer import GameSession


def main():
    pygame.init()
    surf  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("RACER — TSIS 3")
    clock = pygame.time.Clock()

    settings = load_settings()

    # Ask for player name once per launch
    player_name = name_entry_screen(surf, clock)

    while True:
        action = main_menu_screen(surf, clock)

        if action == "quit":
            save_settings(settings)
            pygame.quit()
            sys.exit()

        elif action == "settings":
            settings = settings_screen(surf, clock, settings)
            save_settings(settings)

        elif action == "leaderboard":
            board = load_leaderboard()
            leaderboard_screen(surf, clock, board)

        elif action == "play":
            while True:  # retry loop
                session = GameSession(surf, clock, settings)
                score, distance, coins = session.run()

                # Save to leaderboard
                save_score(player_name, score, distance, coins)

                result = game_over_screen(surf, clock, score, distance, coins)
                if result == "retry":
                    continue
                break  # back to main menu


if __name__ == "__main__":
    main()
