from colorama import Fore, Style, init
from player import Player
from time_machine import TimeMachine
from rooms import random_room
from utils import display_ascii_art, typewriter_effect

def main():
    init()
    player = Player("Hero")
    tm = TimeMachine()
    
    display_ascii_art('start')
    typewriter_effect("Test Game - Move through 3 rooms!", 0.05)
    
    for _ in range(3):
        random_room(player, tm)
    
    typewriter_effect("\nTest completed!", 0.03, Fore.GREEN)

if __name__ == "__main__":
    main()