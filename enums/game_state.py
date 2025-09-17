from enum import Enum

class GameState(Enum):
    MENU = "menu"
    CINEMATIC = "cinematic"
    GAME = "game"
    END = "end"
    QUIT = "quit"