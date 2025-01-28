import random
from time import sleep
from colorama import Fore, Style
from player import Player
from enemy import Enemy, generate_enemy
from puzzles import get_random_puzzle
from colorama import Fore, Style
from time_machine import TimeMachine
from utils import typewriter_effect, display_ascii_art

def combat_room(player, tm):
    """
    Simulates a combat encounter between the player and an enemy.
    """
    # Generate a scaled enemy based on player progress
    difficulty = player.artifacts + 1  # Increase difficulty as player collects artifacts
    enemy = generate_enemy(difficulty)

    typewriter_effect(f"\nYou face the {enemy.name}!", 0.03, Fore.RED)
    while enemy.health > 0 and player.health > 0:
        # Display stats
        typewriter_effect(f"\n{Fore.GREEN}Player Health: {player.health}{Style.RESET_ALL} | {Fore.RED}Enemy Health: {enemy.health}{Style.RESET_ALL}")

        # Player's turn
        action = input("Choose your action (a: attack, d: defend, i: item, r: rewind): ").lower()
        if action == "r":
            previous_state = tm.rewind_time()
            if previous_state:
                player.__dict__ = previous_state
                typewriter_effect("\nTime rewound successfully!", 0.03 ,Fore.CYAN)
            else:
                typewriter_effect("\nNo previous state to rewind to!", 0.03, Fore.YELLOW)
        elif action == "a":
            damage = random.randint(10, 20)
            enemy.health -= damage
            typewriter_effect(f"\nYou dealt {damage} damage to the {enemy.name}!", 0.03, Fore.GREEN)
        elif action == "d":
            typewriter_effect("\nYou brace for the enemy's attack!", 0.03, Fore.YELLOW)
            player.health -= max(enemy.attack_power - random.randint(5, 15), 0)
        elif action == "i":
            item = input("Which item do you want to use? (Health Potion/Time Bomb/Temporal Shield): ").title()
            result = player.use_item(item)
            if result:
                typewriter_effect(f"\n{result}", 0.03,Fore.CYAN)
            else:
                typewriter_effect("\nYou don't have that item or it's invalid!",0.03, Fore.YELLOW)
        else:
            typewriter_effect("\nInvalid action. The enemy attacks!",0.03, Fore.RED)

        # Enemy's turn (if still alive)
        if enemy.health > 0:
            enemy.use_ability(player)
            player.health -= enemy.attack_power
            typewriter_effect(f"\nThe {enemy.name} attacks you for {enemy.attack_power} damage!",0.03, Fore.RED)

    # Combat result
    if player.health > 0:
        typewriter_effect(f"\nYou defeated the {enemy.name} and earned 50 points!",0.03, Fore.GREEN)
        player.score += 50
        typewriter_effect(f"Your current score: {player.score}",0.03, Fore.CYAN)
        return True
    else:
        typewriter_effect("\nYou were defeated... Game Over!",0.03, Fore.RED)
        return False

def puzzle_room(player, tm):
    """
    Simulates a puzzle room where the player must solve a puzzle.
    """
    typewriter_effect("\nYou enter a room filled with ancient mechanisms...",0.03, Fore.CYAN)

    # Get a random puzzle
    puzzle = get_random_puzzle()
    typewriter_effect(f"\nA riddle appears before you:\n{puzzle['question']}",0.03, Fore.YELLOW)

    # Display choices
    for i, choice in enumerate(puzzle["choices"], 1):
        typewriter_effect(f"{i}. {choice}",0.03, Fore.WHITE)

    # Get player's answer
    choice = input("Your answer (or type 'rewind' to go back in time): ").lower()

    if choice == "rewind":
        previous_state = tm.rewind_time()
        if previous_state:
            player.__dict__ = previous_state
            typewriter_effect("\nTime rewound successfully!", 0.03, Fore.CYAN)
        else:
            typewriter_effect("\nNo previous state to rewind to!", 0.03, Fore.YELLOW)
    elif choice == str(puzzle["answer"]):
        typewriter_effect(f"\nCorrect! You solve the puzzle and earn {puzzle['reward']} points!", 0.03,Fore.GREEN)
        player.score += puzzle["reward"]
        typewriter_effect(f"Your current score: {player.score}",0.03, Fore.CYAN)
    else:
        typewriter_effect("\nWrong answer! You feel time slipping away...",0.03, Fore.RED)
        player.health -= 10  # Punishment for wrong answers

    typewriter_effect("\nYou leave the puzzle room feeling wiser—or more confused than ever.",0.03, Fore.CYAN)

def random_event(player, tm):
    """
    Triggers a random event that can occur between rooms.
    """
    events = [
        # Positive Events
        ("You find a hidden stash of treasures! +100 points.", lambda: setattr(player, 'score', player.score + 100)),
        ("A wandering healer restores 20 health.", lambda: setattr(player, 'health', min(player.max_health, player.health + 20))),
        ("You stumble upon a Time Capsule! Gain a new item.", lambda: player.add_item("Mysterious Time Capsule")),
        ("You find a mysterious artifact! +50 points.", lambda: setattr(player, 'score', player.score + 50)),

        # Neutral/Weird Events
        ("A Temporal Storm hits! Your inventory is shuffled.", lambda: random.shuffle(list(player.inventory.keys()))),
        ("A strange figure offers you a cryptic clue for the next puzzle.", lambda: typewriter_effect("The clue whispers: 'Time favors the brave.'", 0.03,Fore.CYAN)),
        ("You find an ancient book that radiates energy. Nothing seems to happen... yet.", lambda: None),

        # Negative Events
        ("You accidentally activate a trap! Lose 15 health.", lambda: setattr(player, 'health', player.health - 15)),
        ("A thief steals 50 points from you!", lambda: setattr(player, 'score', max(0, player.score - 50))),
        ("A Time Rift opens! You're teleported to a random room.", lambda: random_room(player, tm)),
        ("You inhale a strange mist, weakening you. Lose 10 health.", lambda: setattr(player, 'health', player.health - 10))
    ]

    # Select and execute a random event
    event = random.choice(events)
    typewriter_effect(f"\n*** RANDOM EVENT: {event[0]} ***", 0.03, Fore.MAGENTA)
    event[1]()

    # Display updated stats
    if "points" in event[0]:
        typewriter_effect(f"Your current score: {player.score}", 0.03,Fore.CYAN)
    if "health" in event[0]:
        typewriter_effect(f"Your current health: {player.health}",0.03, Fore.GREEN)

def random_room(player, tm):
    """
    Randomly generates a room with a challenge (combat, puzzle, or time anomaly).
    """
    typewriter_effect("\nYou find yourself in a mysterious room filled with ancient mechanisms...", 0.03, Fore.CYAN)


    # Randomly choose between combat, puzzle, or event
    room_type = random.choice(["combat", "puzzle", "event"])

    if room_type == "combat":
        combat_room(player, tm)
    elif room_type == "puzzle":
        puzzle_room(player, tm)
    elif room_type == "event":
        random_event(player, tm)

def boss_battle(player, tm):
    """Final boss battle against Chronos with special time-warping mechanics."""
    boss = Enemy(
        name="Chronos, the Timekeeper",
        health=300,
        attack=35,
        ability=lambda p: (
            typewriter_effect("\nChronos rewinds his own health!",0.03, Fore.RED),
            setattr(boss, 'health', min(300, boss.health + 50))  # Cap health at 300
        )
    )
    
    typewriter_effect("\n*** FINAL SHOWDOWN: CHRONOS, THE TIMEKEEPER ***",0.03, Fore.RED)
    display_ascii_art('boss')
    initial_boss_health = boss.health
    
    # Special boss battle mechanics
    time_vortex = False  # When active, reverses damage taken
    phase = 1

    while boss.health > 0 and player.health > 0:
        typewriter_effect(f"\n{Fore.GREEN}Player Health: {player.health}{Style.RESET_ALL} | "
                         f"{Fore.RED}Boss Health: {boss.health}{Style.RESET_ALL} | "
                         f"{Fore.YELLOW}Phase: {phase}{Style.RESET_ALL}")

        # Player's turn
        action = input("Choose your action (a: attack, d: defend, i: item, r: rewind): ").lower()
        
        if action == "r":
            previous_state = tm.rewind_time()
            if previous_state:
                player.__dict__ = previous_state
                boss.health = initial_boss_health  # Reset boss health on rewind
                phase = 1
                time_vortex = False
                typewriter_effect("\nTime rewound to start of battle!",0.03, Fore.CYAN)
                continue
            else:
                typewriter_effect("\nNo previous state to rewind to!",0.03, Fore.YELLOW)
        elif action == "a":
            damage = random.randint(15, 25)
            if time_vortex:
                player.health -= damage
                typewriter_effect(f"\nTime vortex reverses your attack! You take {damage} damage!",0.03, Fore.MAGENTA)
            else:
                boss.health -= damage
                typewriter_effect(f"\nYou dealt {damage} damage to Chronos!",0.03, Fore.GREEN)
        elif action == "d":
            typewriter_effect("\nYou brace for Chronos's attack!",0.03, Fore.YELLOW)
        elif action == "i":
            item = input("Which item? (Health Potion/Time Bomb/Temporal Shield): ").title()
            result = player.use_item(item)
            if result:
                typewriter_effect(f"\n{result}",0.03,Fore.CYAN)
                if item == "Time Bomb":
                    boss.health -= 40
                    typewriter_effect("The Time Bomb explodes in Chronos' face!",0.03, Fore.RED)
                elif item == "Temporal Shield":
                    time_vortex = False  # Disable time vortex
            else:
                typewriter_effect("\nInvalid item or none left!", 0.03,Fore.YELLOW)
        else:
            typewriter_effect("\nInvalid action! Chronos capitalizes on your hesitation!",0.03, Fore.RED)

        # Boss phase transitions
        if boss.health <= 200 and phase == 1:
            phase = 2
            typewriter_effect("\nChronos: \"You dare challenge time itself?\"",0.03, Fore.RED)
            typewriter_effect("Phase 2: Chronos now heals more frequently!", 0.03,Fore.MAGENTA)
            
        if boss.health <= 100 and phase == 2:
            phase = 3
            typewriter_effect("\nChronos: \"Witness the true power of time!\"",0.03, Fore.RED)
            typewriter_effect("Phase 3: Time Vortex activated - attacks may backfire!",0.03, Fore.MAGENTA)
            time_vortex = True

        # Boss's turn
        if boss.health > 0:
            # Boss uses ability every 2 turns
            if phase >= 2 and random.random() < 0.5:
                boss.use_ability(player)
                
            damage = boss.attack_power + (phase * 5)
            if action == "d":
                damage = max(damage - random.randint(10, 20), 5)
                
            player.health -= damage
            typewriter_effect(f"\nChronos attacks with temporal energy for {damage} damage!", 0.03,Fore.RED)

    # Battle conclusion
    if player.health > 0:
        player.artifacts = 3  # Auto-collect remaining artifacts for victory
        return True
    return False