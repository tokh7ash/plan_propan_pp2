"""main.py — entry point for Snake TSIS-3."""
import sys
import os
import io

# ── Step 1: fix encoding BEFORE anything else ─────────────────────────────────
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["LC_ALL"]           = "C"
os.environ["LC_MESSAGES"]      = "C"
os.environ["LANG"]             = "C"
os.environ["PYTHONIOENCODING"] = "utf-8"

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import settings1
import db
from ui import (name_entry_screen, main_menu_screen, settings_screen,
                leaderboard_screen, game_over_screen)
from game import GameSession
from config import WIDTH, HEIGHT


def main():
    pygame.init()
    surf  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake - TSIS 3")
    clock = pygame.time.Clock()

    settings = settings1.load()

    db_ok = db.init_db()
    if not db_ok:
        print("[INFO] PostgreSQL not available - leaderboard disabled.")

    username      = name_entry_screen(surf, clock)
    personal_best = db.get_personal_best(username) if db_ok else 0

    while True:
        action = main_menu_screen(surf, clock, personal_best)

        if action == "quit":
            settings1.save(settings)
            pygame.quit()
            sys.exit()

        elif action == "settings":
            settings = settings_screen(surf, clock, settings)
            settings1.save(settings)

        elif action == "leaderboard":
            board = db.get_leaderboard() if db_ok else []
            leaderboard_screen(surf, clock, board)

        elif action == "play":
            while True:
                session = GameSession(surf, clock, settings, personal_best)
                score, level = session.run()

                if db_ok:
                    db.save_session(username, score, level)
                    personal_best = db.get_personal_best(username)
                else:
                    personal_best = max(personal_best, score)

                result = game_over_screen(surf, clock, score, level, personal_best)
                if result == "retry":
                    continue
                break


if __name__ == "__main__":
    main()