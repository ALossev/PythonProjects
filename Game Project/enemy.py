import random

from colorama import Fore

from utils import typewriter_effect

class Enemy:
    def __init__(self, name, health, attack, ability=None):
        self.name = name
        self.health = health
        self.attack_power = attack
        self.ability = ability

    def use_ability(self, player):
        if self.ability:
            self.ability(player)

def generate_enemy(difficulty):
    """Generates an enemy with stats based on difficulty."""
    base_health = 50 + (difficulty * 20)
    base_attack = 10 + (difficulty * 5)
    abilities = [
        lambda p: typewriter_effect(f"The {p.name} freezes time! You lose your turn!",0.03, Fore.BLUE),
        lambda p: setattr(p, 'health', max(p.health - 10, 0)),
        lambda p: typewriter_effect(f"The {p.name} dodges your attack!", 0.03,Fore.YELLOW)
    ]
    return Enemy(
        name=f"Level {difficulty} Enemy",
        health=base_health,
        attack=base_attack,
        ability=random.choice(abilities)
    )