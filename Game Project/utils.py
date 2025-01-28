import time
import sys
from colorama import Fore, Style

def typewriter_effect(text, delay=0.03, color=Fore.WHITE):
    """Simulates a typewriter effect with colored text."""
    # Ensure delay is a number (float or int)
    delay = float(delay)  # Converts the delay to a float if it's a string
    for char in text:
        sys.stdout.write(color + char + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_ascii_art(art_name):
    """
    Displays ASCII art based on the art name.
    
    Args:
        art_name (str): The key name of the ASCII art to display.
    """
    arts = {
        'start': r"""
8888888b.                        888                         
888   Y88b                       888                         
888    888                       888                         
888   d88P 8888b.  88888b.   .d88888  .d88b.  888d888 8888b. 
8888888P"     "88b 888 "88b d88" 888 d88""88b 888P"      "88b
888       .d888888 888  888 888  888 888  888 888    .d888888
888       888  888 888  888 Y88b 888 Y88..88P 888    888  888
888       "Y888888 888  888  "Y88888  "Y88P"  888    "Y888888

****************************************************************
*                                                              *
*                       Welcome to Pandora!                    *
*                                                              *
*        A place where secrets, surprises, and mysteries       *
*                   are waiting to be unlocked.                *
*                                                              *
****************************************************************
""",
        'boss': r"""
 ******************************************************************
* ____                  ____                                     *
*| __ )  ___  ___ ___  |  _ \ _   _ _ __   __ _  ___  ___  _ __  *
*|  _ \ / _ \/ __/ __| | | | | | | | '_ \ / _` |/ _ \/ _ \| '_ \ *
*| |_) | (_) \__ \__ \ | |_| | |_| | | | | (_| |  __/ (_) | | | |*
*|____/ \___/|___/___/ |____/ \__,_|_| |_|\__, |\___|\___/|_| |_|*
*                                         |___/                  *
******************************************************************
""",
    }
    print(arts.get(art_name, "No ASCII art found for this key."))