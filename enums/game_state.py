from enum import Enum

class GameState(Enum):
    MENU = "menu"
    GAME = "game"
    END = "end"
    QUIT = "quit"
    
    CINEMATIC = "cinematic"