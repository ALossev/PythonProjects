import random
import time
import os
import sys
from enum import Enum
from collections import Counter
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

# Color codes for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'
    
    # Card colors
    HEARTS = '\033[91m'    # Red
    DIAMONDS = '\033[91m'  # Red
    CLUBS = '\033[90m'     # Black
    SPADES = '\033[90m'    # Black

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def animated_text(text, color=Colors.WHITE):
    print(f"{color}{text}{Colors.END}")
    time.sleep(0.5)

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Card:
    def __init__(self, rank: int, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def get_color(self):
        if self.suit in [Suit.HEARTS, Suit.DIAMONDS]:
            return Colors.HEARTS
        else:
            return Colors.CLUBS
    
    def __str__(self):
        rank_names = {1: "A", 11: "J", 12: "Q", 13: "K"}
        rank_str = rank_names.get(self.rank, str(self.rank))
        color = self.get_color()
        return f"{color}{rank_str}{self.suit.value}{Colors.END}"
    
    def get_ascii_card(self):
        rank_names = {1: "A", 11: "J", 12: "Q", 13: "K"}
        rank_str = rank_names.get(self.rank, str(self.rank)).rjust(2)
        color = self.get_color()
        
        return [
            "┌─────────┐",
            f"│{color}{rank_str}{Colors.END}       │",
            "│         │",
            f"│    {color}{self.suit.value}{Colors.END}    │",
            "│         │",
            f"│       {color}{rank_str}{Colors.END}│",
            "└─────────┘"
        ]
    
    def __repr__(self):
        return str(self)

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in range(1, 14)]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self, count=1):
        drawn = []
        for _ in range(min(count, len(self.cards))):
            if self.cards:
                drawn.append(self.cards.pop())
        return drawn

class PokerHand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda x: x.rank, reverse=True)
        self.rank, self.value = self._evaluate()
    
    def _evaluate(self) -> Tuple[HandRank, List[int]]:
        ranks = [card.rank for card in self.cards]
        suits = [card.suit for card in self.cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(ranks)
        
        if ranks == [13, 4, 3, 2, 1]:  # A-2-3-4-5
            is_straight = True
            ranks = [4, 3, 2, 1, 0]
        
        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), key=rank_counts.get, reverse=True)
        
        if is_straight and is_flush:
            if ranks[0] == 13 and ranks[1] == 12:
                return HandRank.ROYAL_FLUSH, [14]
            return HandRank.STRAIGHT_FLUSH, [max(ranks)]
        
        if counts == [4, 1]:
            return HandRank.FOUR_KIND, unique_ranks
        
        if counts == [3, 2]:
            return HandRank.FULL_HOUSE, unique_ranks
        
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)
        
        if is_straight:
            return HandRank.STRAIGHT, [max(ranks)]
        
        if counts == [3, 1, 1]:
            return HandRank.THREE_KIND, unique_ranks
        
        if counts == [2, 2, 1]:
            return HandRank.TWO_PAIR, unique_ranks
        
        if counts == [2, 1, 1, 1]:
            return HandRank.PAIR, unique_ranks
        
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)
    
    def _is_straight(self, ranks: List[int]) -> bool:
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) != 5:
            return False
        return sorted_ranks[-1] - sorted_ranks[0] == 4
    
    def __gt__(self, other):
        if self.rank != other.rank:
            return self.rank.value > other.rank.value
        return self.value > other.value
    
    def get_colored_name(self):
        colors = {
            HandRank.ROYAL_FLUSH: Colors.MAGENTA + Colors.BOLD,
            HandRank.STRAIGHT_FLUSH: Colors.CYAN + Colors.BOLD,
            HandRank.FOUR_KIND: Colors.RED + Colors.BOLD,
            HandRank.FULL_HOUSE: Colors.GREEN + Colors.BOLD,
            HandRank.FLUSH: Colors.BLUE + Colors.BOLD,
            HandRank.STRAIGHT: Colors.YELLOW + Colors.BOLD,
            HandRank.THREE_KIND: Colors.GREEN,
            HandRank.TWO_PAIR: Colors.YELLOW,
            HandRank.PAIR: Colors.CYAN,
            HandRank.HIGH_CARD: Colors.WHITE
        }
        color = colors.get(self.rank, Colors.WHITE)
        return f"{color}{self.rank.name.replace('_', ' ').title()}{Colors.END}"
    
    def __str__(self):
        return f"{self.get_colored_name()}: {' '.join(str(card) for card in self.cards)}"

class Item:
    def __init__(self, name: str, description: str, effect: str, value: int):
        self.name = name
        self.description = description
        self.effect = effect  # 'luck', 'chip_bonus', 'hand_bonus', etc.
        self.value = value
        self.used = False
    
    def __str__(self):
        return f"{Colors.YELLOW}{self.name}{Colors.END}: {self.description}"

class GameStats:
    def __init__(self):
        self.hands_played = 0
        self.hands_won = 0
        self.enemies_defeated = 0
        self.highest_level = 0
        self.total_chips_won = 0
        self.best_hand = None
        self.lucky_escapes = 0
        self.perfect_games = 0
    
    def win_rate(self):
        return (self.hands_won / self.hands_played * 100) if self.hands_played > 0 else 0

class Enemy:
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level
        self.chips = 50 + (level * 25)
        self.aggression = min(0.3 + (level * 0.1), 0.8)
        self.bluff_rate = min(0.1 + (level * 0.05), 0.4)
        self.special_ability = self._get_special_ability()
        self.ability_used = False
    
    def _get_special_ability(self):
        abilities = {
            1: None,
            2: "Lucky Draw",  # Can redraw one card
            3: "Intimidation",  # Forces minimum bet
            4: "Card Counting",  # Higher accuracy in decisions
            5: "Bluff Master",  # Increased bluff success
            6: "Shadow Step",  # Can skip one betting round
            7: "Blood Drain",  # Steals chips on win
            8: "Hellfire",  # Burns player's worst card
            9: "Dragon Rage",  # All-in more likely
            10: "Death Magic"  # Revive once with half chips
        }
        return abilities.get(self.level)
    
    def get_ascii_art(self):
        arts = {
            "Bandit": [
                "    🗡️ 💰",
                "   \\ 😠 /",
                "    \\   /",
                "     \\ /"
            ],
            "Rogue": [
                "   🏹 🗡️",
                "   \\ 😏 /",
                "    \\   /",
                "     \\ /"
            ],
            "Mercenary": [
                "   ⚔️ 🛡️",
                "   \\ 😤 /",
                "    \\   /",
                "     \\ /"
            ],
            "Assassin": [
                "   🗡️ 🌙",
                "   \\ 😈 /",
                "    \\   /",
                "     \\ /"
            ],
            "Warlord": [
                "   👑 ⚔️",
                "   \\ 😠 /",
                "    \\   /",
                "     \\ /"
            ],
            "Shadow": [
                "   👻 🌙",
                "   \\ 😶 /",
                "    \\   /",
                "     \\ /"
            ],
            "Vampire": [
                "   🦇 🩸",
                "   \\ 🧛 /",
                "    \\   /",
                "     \\ /"
            ],
            "Demon": [
                "   🔥 😈",
                "   \\ 👹 /",
                "    \\   /",
                "     \\ /"
            ],
            "Dragon": [
                "  🔥 🐲 🔥",
                "   \\   /",
                "    \\ /",
                "     V"
            ],
            "Lich": [
                "   💀 ⚡",
                "   \\ 🧙 /",
                "    \\   /",
                "     \\ /"
            ]
        }
        
        enemy_type = self.name.split()[0]
        return arts.get(enemy_type, [
            "   ⚔️ 🛡️",
            "   \\ 😤 /",
            "    \\   /",
            "     \\ /"
        ])
    
    def use_special_ability(self, game_state):
        if self.ability_used or not self.special_ability:
            return None
        
        self.ability_used = True
        return self.special_ability
    
    def decide_action(self, hand_strength: float, pot: int, to_call: int) -> str:
        # Enhanced AI with more sophisticated decision making
        chip_ratio = to_call / max(self.chips, 1)
        pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 0
        
        # Adjust for aggression and level
        aggression_modifier = self.aggression * (1 + self.level * 0.05)
        
        if hand_strength > 0.8:
            if random.random() < 0.7:
                return "raise"
            else:
                return "call"
        elif hand_strength > 0.6:
            if chip_ratio < 0.2 or pot_odds > hand_strength:
                return "call" if to_call > 0 else "check"
            elif random.random() < aggression_modifier:
                return "raise"
            else:
                return "call" if to_call > 0 else "check"
        elif hand_strength > 0.3:
            if to_call == 0:
                return "check"
            elif pot_odds > hand_strength and chip_ratio < 0.1:
                return "call"
            elif random.random() < self.bluff_rate:
                return "raise" if random.random() < 0.4 else "call"
            else:
                return "fold"
        else:
            if random.random() < self.bluff_rate * aggression_modifier:
                return "raise" if random.random() < 0.3 else "call"
            elif to_call == 0:
                return "check"
            else:
                return "fold"

def display_cards_horizontal(cards):
    """Display cards side by side"""
    if not cards:
        return
    
    card_lines = [card.get_ascii_card() for card in cards]
    
    # Print each line of all cards
    for line_idx in range(7):  # Cards are 7 lines tall
        line = ""
        for card_art in card_lines:
            line += card_art[line_idx] + " "
        print(line)

def display_title():
    title = f"""
{Colors.RED + Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🎰 ROGUELIKE POKER 🎰                     ║
║                                                              ║
║           🗡️  Battle through the card realm!  ⚔️             ║
║                   Enhanced Edition                           ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
    """
    print(title)

def display_level_banner(level):
    banner = f"""
{Colors.YELLOW + Colors.BOLD}
    ╔═══════════════════════════════════════════════════╗
    ║                    LEVEL {level:2d}                     ║
    ╚═══════════════════════════════════════════════════╝
{Colors.END}
    """
    print(banner)

def display_pot_and_chips(pot, player_chips, enemy_chips=None, enemy_name=""):
    pot_display = f"""
{Colors.CYAN}┌─────────────────────────────────────────────┐
│  💰 POT: {Colors.YELLOW + Colors.BOLD}{pot:,} chips{Colors.CYAN}                      │
│                                             │
│  🎯 Your chips: {Colors.GREEN + Colors.BOLD}{player_chips:,}{Colors.CYAN}                      │"""
    
    if enemy_chips is not None:
        pot_display += f"""
│  ⚔️  {enemy_name} chips: {Colors.RED + Colors.BOLD}{enemy_chips:,}{Colors.CYAN}              │"""
    
    pot_display += f"""
└─────────────────────────────────────────────┘{Colors.END}"""
    
    print(pot_display)

def display_inventory(items):
    if not items:
        print(f"{Colors.GRAY}🎒 Inventory: Empty{Colors.END}")
        return
    
    print(f"{Colors.YELLOW + Colors.BOLD}🎒 INVENTORY:{Colors.END}")
    for i, item in enumerate(items, 1):
        status = f"{Colors.GRAY}(used){Colors.END}" if item.used else f"{Colors.GREEN}(ready){Colors.END}"
        print(f"  {i}. {item} {status}")

class RoguelikePoker:
    def __init__(self):
        self.player_chips = 100
        self.level = 1
        self.victories = 0
        self.deck = Deck()
        self.inventory = []
        self.stats = GameStats()
        self.difficulty = "normal"
        self.reset_game()
        self.load_high_score()
    
    def reset_game(self):
        self.pot = 0
        self.player_bet = 0
        self.enemy_bet = 0
        self.player_hand = []
        self.enemy_hand = []
        self.community_cards = []
        self.game_phase = "pre_flop"
        self.deck.reset()
    
    def load_high_score(self):
        try:
            with open("poker_save.json", "r") as f:
                data = json.load(f)
                self.high_score = data.get("high_score", 0)
                self.best_run_stats = data.get("best_run_stats", {})
        except FileNotFoundError:
            self.high_score = 0
            self.best_run_stats = {}
    
    def save_high_score(self):
        try:
            data = {
                "high_score": max(self.high_score, self.level),
                "best_run_stats": self.best_run_stats if self.level > self.high_score else {
                    "level": self.level,
                    "chips": self.player_chips,
                    "hands_won": self.stats.hands_won,
                    "win_rate": self.stats.win_rate(),
                    "date": datetime.now().isoformat()
                }
            }
            with open("poker_save.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"{Colors.RED}Could not save progress: {e}{Colors.END}")
    
    def add_item(self, item):
        self.inventory.append(item)
        animated_text(f"🎁 Found: {item.name}!", Colors.YELLOW)
    
    def use_item(self, item_index):
        if 0 <= item_index < len(self.inventory):
            item = self.inventory[item_index]
            if not item.used:
                item.used = True
                return self.apply_item_effect(item)
        return False
    
    def apply_item_effect(self, item):
        if item.effect == "luck":
            # Get a slight hand strength bonus for this round
            animated_text(f"✨ {item.name} grants you luck!", Colors.YELLOW)
            return "luck_boost"
        elif item.effect == "chip_bonus":
            self.player_chips += item.value
            animated_text(f"💰 {item.name} grants you {item.value} chips!", Colors.GREEN)
            return "chips"
        elif item.effect == "heal":
            heal_amount = min(item.value, 200 - self.player_chips)
            self.player_chips += heal_amount
            animated_text(f"💊 {item.name} restores {heal_amount} chips!", Colors.GREEN)
            return "heal"
        return False
    
    def generate_random_item(self):
        items = [
            Item("Lucky Charm", "Slightly improves hand strength", "luck", 1),
            Item("Coin Pouch", "Grants 25 chips", "chip_bonus", 25),
            Item("Magic Elixir", "Restores health", "heal", 50),
            Item("Rabbit's Foot", "Major luck boost", "luck", 2),
            Item("Golden Coin", "Grants 50 chips", "chip_bonus", 50),
            Item("Phoenix Feather", "Full health restoration", "heal", 100),
        ]
        return random.choice(items)
    
    def show_stats(self):
        print(f"\n{Colors.CYAN + Colors.BOLD}📊 GAME STATISTICS{Colors.END}")
        print(f"Hands played: {self.stats.hands_played}")
        print(f"Hands won: {self.stats.hands_won}")
        print(f"Win rate: {self.stats.win_rate():.1f}%")
        print(f"Enemies defeated: {self.stats.enemies_defeated}")
        print(f"Current level: {self.level}")
        print(f"High score: {self.high_score}")
        print(f"Total chips won: {self.stats.total_chips_won:,}")
    
    def difficulty_selection(self):
        print(f"\n{Colors.BOLD}⚙️  SELECT DIFFICULTY:{Colors.END}")
        print(f"1. {Colors.GREEN}Easy{Colors.END} - More chips, weaker enemies")
        print(f"2. {Colors.YELLOW}Normal{Colors.END} - Balanced gameplay")
        print(f"3. {Colors.RED}Hard{Colors.END} - Fewer chips, stronger enemies")
        print(f"4. {Colors.MAGENTA}Nightmare{Colors.END} - Ultimate challenge")
        
        while True:
            choice = input(f"{Colors.CYAN}Choose difficulty (1-4): {Colors.END}").strip()
            if choice == "1":
                self.difficulty = "easy"
                self.player_chips = 150
                break
            elif choice == "2":
                self.difficulty = "normal"
                self.player_chips = 100
                break
            elif choice == "3":
                self.difficulty = "hard"
                self.player_chips = 75
                break
            elif choice == "4":
                self.difficulty = "nightmare"
                self.player_chips = 50
                break
            else:
                print(f"{Colors.RED}Invalid choice!{Colors.END}")
    
    def deal_hands(self):
        self.player_hand = self.deck.draw(2)
        self.enemy_hand = self.deck.draw(2)
    
    def deal_flop(self):
        self.deck.draw(1)
        self.community_cards.extend(self.deck.draw(3))
        self.game_phase = "flop"
    
    def deal_turn(self):
        self.deck.draw(1)
        self.community_cards.extend(self.deck.draw(1))
        self.game_phase = "turn"
    
    def deal_river(self):
        self.deck.draw(1)
        self.community_cards.extend(self.deck.draw(1))
        self.game_phase = "river"
    
    def get_best_hand(self, hole_cards: List[Card]) -> PokerHand:
        all_cards = hole_cards + self.community_cards
        if len(all_cards) < 5:
            return PokerHand(hole_cards + [Card(2, Suit.HEARTS)] * (5 - len(hole_cards)))
        
        from itertools import combinations
        best_hand = None
        
        for combo in combinations(all_cards, 5):
            hand = PokerHand(list(combo))
            if best_hand is None or hand > best_hand:
                best_hand = hand
        
        return best_hand
    
    def evaluate_hand_strength(self, hole_cards: List[Card], luck_boost=False) -> float:
        if not self.community_cards:
            ranks = sorted([card.rank for card in hole_cards], reverse=True)
            if ranks[0] == ranks[1]:
                strength = min(0.5 + (ranks[0] / 26), 0.95)
            elif ranks[0] >= 10 or (ranks[0] >= 7 and ranks[1] >= 7):
                strength = 0.4 + (sum(ranks) / 52)
            else:
                strength = 0.1 + (sum(ranks) / 78)
        else:
            best_hand = self.get_best_hand(hole_cards)
            base_strength = best_hand.rank.value / 10.0
            
            if best_hand.rank in [HandRank.HIGH_CARD, HandRank.PAIR]:
                kicker_bonus = sum(best_hand.value[:2]) / 52.0
                strength = min(base_strength + kicker_bonus, 0.95)
            else:
                strength = min(base_strength, 0.95)
        
        if luck_boost:
            strength = min(strength + 0.15, 0.98)
        
        return strength
    
    def display_game_state(self, enemy):
        clear_screen()
        display_title()
        display_level_banner(self.level)
        display_pot_and_chips(self.pot, self.player_chips, enemy.chips, enemy.name)
        
        print(f"\n{Colors.BOLD}🃏 PHASE: {self.game_phase.upper().replace('_', '-')}{Colors.END}")
        
        if hasattr(self, 'high_score') and self.high_score > 0:
            print(f"{Colors.GRAY}🏆 Best: Level {self.high_score}{Colors.END}")
        
        # Enemy display
        print(f"\n{Colors.RED + Colors.BOLD}⚔️  {enemy.name}{Colors.END}")
        if enemy.special_ability and not enemy.ability_used:
            print(f"{Colors.MAGENTA}🔮 Special: {enemy.special_ability}{Colors.END}")
        
        enemy_art = enemy.get_ascii_art()
        for line in enemy_art:
            print(f"    {line}")
        
        # Community cards
        if self.community_cards:
            print(f"\n{Colors.YELLOW + Colors.BOLD}🏛️  COMMUNITY CARDS{Colors.END}")
            display_cards_horizontal(self.community_cards)
        
        # Player hand with strength indicator
        print(f"\n{Colors.GREEN + Colors.BOLD}🎯 YOUR HAND{Colors.END}")
        display_cards_horizontal(self.player_hand)
        
        # Hand strength indicator
        if self.community_cards:
            strength = self.evaluate_hand_strength(self.player_hand)
            strength_bar = "█" * int(strength * 10) + "░" * (10 - int(strength * 10))
            strength_color = Colors.GREEN if strength > 0.6 else Colors.YELLOW if strength > 0.3 else Colors.RED
            print(f"💪 Hand Strength: {strength_color}{strength_bar}{Colors.END} ({strength:.1%})")
        
        # Inventory
        display_inventory(self.inventory)
        
        # Show best hands during showdown
        if self.game_phase == "showdown":
            print(f"\n{Colors.RED + Colors.BOLD}⚔️  {enemy.name.upper()} HAND{Colors.END}")
            display_cards_horizontal(self.enemy_hand)
            
            player_best = self.get_best_hand(self.player_hand)
            enemy_best = self.get_best_hand(self.enemy_hand)
            
            print(f"\n{Colors.GREEN + Colors.BOLD}🎯 Your Best Hand: {Colors.END}{player_best}")
            print(f"{Colors.RED + Colors.BOLD}⚔️  Enemy Best Hand: {Colors.END}{enemy_best}")
    
    def animated_deal(self, phase_name):
        print(f"\n{Colors.CYAN + Colors.BOLD}🎴 Dealing {phase_name}...{Colors.END}")
        for i in range(3):
            print("🎴" * (i + 1))
            time.sleep(0.3)
        print(f"{Colors.GREEN}✨ {phase_name} dealt!{Colors.END}")
        time.sleep(0.5)
    
    def betting_round(self, enemy: Enemy) -> bool:
        to_call = self.enemy_bet - self.player_bet
        luck_boost = False
        
        while True:
            print(f"\n{Colors.YELLOW + Colors.BOLD}💸 BETTING ROUND{Colors.END}")
            
            if to_call > 0:
                print(f"💰 To call: {Colors.RED + Colors.BOLD}{to_call}{Colors.END} chips")
            
            # Show available actions
            actions = []
            if to_call > 0:
                actions.extend(["call", "raise", "fold"])
            else:
                actions.extend(["check", "bet", "fold"])
            
            if self.inventory and any(not item.used for item in self.inventory):
                actions.append("item")
            
            action_str = "/".join(actions)
            action = input(f"{Colors.CYAN}🎯 Action ({action_str}): {Colors.END}").lower().strip()
            
            if action == "fold":
                animated_text("🏳️  You fold.", Colors.RED)
                return False
            
            elif action == "item":
                self.show_inventory_menu()
                continue
            
            elif action in ["call", "check"]:
                if action == "call" and to_call > 0:
                    if self.player_chips < to_call:
                        animated_text(f"❌ Not enough chips! You need {to_call} but have {self.player_chips}", Colors.RED)
                        continue
                    self.player_chips -= to_call
                    self.pot += to_call
                    self.player_bet = self.enemy_bet
                
                animated_text(f"✅ You {action}.", Colors.GREEN)
                break
            
            elif action in ["bet", "raise"]:
                try:
                    print(f"Suggested bets: {Colors.GRAY}[{max(10, to_call)}] [{max(25, to_call*2)}] [{max(50, self.player_chips//4)}]{Colors.END}")
                    amount_input = input(f"💰 Amount (max {self.player_chips}): ").strip()
                    
                    if not amount_input:
                        continue
                    
                    amount = int(amount_input)
                    if amount <= 0:
                        animated_text("❌ Bet must be positive.", Colors.RED)
                        continue
                    if amount > self.player_chips:
                        animated_text("❌ Not enough chips!", Colors.RED)
                        continue
                    
                    total_bet = to_call + amount
                    if self.player_chips < total_bet:
                        animated_text("❌ Not enough chips for that bet!", Colors.RED)
                        continue
                    
                    self.player_chips -= total_bet
                    self.pot += total_bet
                    self.player_bet += total_bet
                    
                    animated_text(f"🚀 You {'raise' if to_call > 0 else 'bet'} {amount}!", Colors.YELLOW)
                    
                    # Enemy response with suspense
                    print(f"\n{Colors.MAGENTA}🤔 {enemy.name} is thinking...{Colors.END}")
                    time.sleep(1.5)
                    
                    # Check if enemy uses special ability
                    special = enemy.use_special_ability(None)
                    if special and not enemy.ability_used:
                        animated_text(f"🔮 {enemy.name} uses {special}!", Colors.MAGENTA)
                        time.sleep(1)
                    
                    enemy_strength = self.evaluate_hand_strength(self.enemy_hand)
                    enemy_action = enemy.decide_action(enemy_strength, self.pot, amount)
                    
                    if enemy_action == "fold":
                        animated_text(f"🏳️  {enemy.name} folds.", Colors.GREEN)
                        return True
                    elif enemy_action == "call":
                        if enemy.chips >= amount:
                            enemy.chips -= amount
                            self.pot += amount
                            self.enemy_bet = self.player_bet
                            animated_text(f"💪 {enemy.name} calls.", Colors.YELLOW)
                        else:
                            animated_text(f"💸 {enemy.name} doesn't have enough chips and folds.", Colors.GREEN)
                        return True
                    elif enemy_action == "raise":
                        raise_amount = min(amount * 2, enemy.chips)
                        enemy.chips -= raise_amount
                        self.pot += raise_amount
                        self.enemy_bet += raise_amount
                        animated_text(f"🔥 {enemy.name} raises to {raise_amount}!", Colors.RED)
                        to_call = self.enemy_bet - self.player_bet
                        continue
                    
                    break
                    
                except ValueError:
                    animated_text("❌ Please enter a valid number.", Colors.RED)
            
            else:
                animated_text("❌ Invalid action. Use the available options.", Colors.RED)
        
        return True
    
    def show_inventory_menu(self):
        if not self.inventory:
            animated_text("🎒 Your inventory is empty.", Colors.GRAY)
            return
        
        print(f"\n{Colors.YELLOW + Colors.BOLD}🎒 INVENTORY MENU{Colors.END}")
        usable_items = [i for i, item in enumerate(self.inventory) if not item.used]
        
        if not usable_items:
            animated_text("All items have been used.", Colors.GRAY)
            return
        
        for idx in usable_items:
            print(f"  {idx + 1}. {self.inventory[idx]}")
        
        try:
            choice = input(f"{Colors.CYAN}Use item (number or 'back'): {Colors.END}").strip()
            if choice.lower() == 'back':
                return
            
            item_idx = int(choice) - 1
            if item_idx in usable_items:
                effect = self.use_item(item_idx)
                if effect == "luck_boost":
                    return "luck_boost"
            else:
                animated_text("❌ Invalid item or already used.", Colors.RED)
        except ValueError:
            animated_text("❌ Please enter a valid number or 'back'.", Colors.RED)
        
        return None
    
    def play_hand(self, enemy: Enemy) -> bool:
        self.reset_game()
        self.deal_hands()
        self.stats.hands_played += 1
        luck_boost = False
        
        # Pre-flop
        self.display_game_state(enemy)
        animated_text("🎴 Cards dealt! Let the battle begin!", Colors.CYAN)
        
        result = self.betting_round(enemy)
        if not result:
            enemy.chips += self.pot
            return False
        if result == "luck_boost":
            luck_boost = True
        
        # Flop
        self.animated_deal("FLOP")
        self.deal_flop()
        self.display_game_state(enemy)
        
        if not self.betting_round(enemy):
            enemy.chips += self.pot
            return False
        
        # Turn
        self.animated_deal("TURN")
        self.deal_turn()
        self.display_game_state(enemy)
        
        if not self.betting_round(enemy):
            enemy.chips += self.pot
            return False
        
        # River
        self.animated_deal("RIVER")
        self.deal_river()
        self.display_game_state(enemy)
        
        if not self.betting_round(enemy):
            enemy.chips += self.pot
            return False
        
        # Showdown
        self.game_phase = "showdown"
        animated_text("⚔️  SHOWDOWN TIME!", Colors.MAGENTA + Colors.BOLD)
        self.display_game_state(enemy)
        
        player_best = self.get_best_hand(self.player_hand)
        enemy_best = self.get_best_hand(self.enemy_hand)
        
        # Apply luck boost if active
        if luck_boost and player_best.rank.value <= enemy_best.rank.value:
            if random.random() < 0.3:  # 30% chance for luck to save you
                animated_text("✨ Your luck saves you! Cards reshuffled in your favor!", Colors.YELLOW)
                self.stats.lucky_escapes += 1
                # Artificially boost player hand for this calculation
                player_wins = True
            else:
                player_wins = player_best > enemy_best
        else:
            player_wins = player_best > enemy_best
        
        print(f"\n{Colors.BOLD}🎯 Comparing hands...{Colors.END}")
        time.sleep(2)
        
        # Update stats for best hand tracking
        if not self.stats.best_hand or player_best.rank.value > self.stats.best_hand.rank.value:
            self.stats.best_hand = player_best
        
        if player_wins:
            victory_text = f"""
{Colors.GREEN + Colors.BOLD}
    🎉 ✨ VICTORY! ✨ 🎉
    
    You win {self.pot} chips!
{Colors.END}"""
            print(victory_text)
            self.player_chips += self.pot
            self.stats.hands_won += 1
            self.stats.total_chips_won += self.pot
            
            # Chance for item drop
            if random.random() < 0.3:
                item = self.generate_random_item()
                self.add_item(item)
            
            return True
        elif not player_wins and player_best.rank != enemy_best.rank:
            defeat_text = f"""
{Colors.RED + Colors.BOLD}
    💀 DEFEAT! 💀
    
    {enemy.name} wins {self.pot} chips!
{Colors.END}"""
            print(defeat_text)
            enemy.chips += self.pot
            return False
        else:
            tie_text = f"""
{Colors.YELLOW + Colors.BOLD}
    🤝 TIE! 🤝
    
    Pot is split!
{Colors.END}"""
            print(tie_text)
            self.player_chips += self.pot // 2
            enemy.chips += self.pot - (self.pot // 2)
            return True
    
    def level_up(self):
        self.level += 1
        self.victories += 1
        self.stats.enemies_defeated += 1
        self.stats.highest_level = max(self.stats.highest_level, self.level)
        
        # Difficulty-based rewards
        multipliers = {"easy": 1.0, "normal": 1.2, "hard": 1.5, "nightmare": 2.0}
        multiplier = multipliers.get(self.difficulty, 1.0)
        
        bonus_chips = int((50 + (self.level * 10)) * multiplier)
        self.player_chips += bonus_chips
        
        level_up_art = f"""
{Colors.YELLOW + Colors.BOLD}
    ✨🎉✨🎉✨🎉✨🎉✨🎉✨🎉✨
    🎉                           🎉
    ✨    🆙 LEVEL UP! 🆙         ✨
    🎉                           🎉
    ✨   Level: {self.level:2d}              ✨
    🎉   Bonus: +{bonus_chips} chips        🎉
    ✨   Total: {self.player_chips:,} chips       ✨
    🎉   Difficulty: {self.difficulty.title():>10}   🎉
    ✨🎉✨🎉✨🎉✨🎉✨🎉✨🎉✨
{Colors.END}"""
        
        clear_screen()
        print(level_up_art)
        
        # Recovery bonus for low health
        if self.player_chips < 50:
            heal = 30
            self.player_chips += heal
            print(f"{Colors.GREEN}💊 Recovery bonus: +{heal} chips{Colors.END}")
        
        # Perfect game bonus (didn't lose a single hand)
        if hasattr(self, 'perfect_game_tracker') and self.perfect_game_tracker:
            self.stats.perfect_games += 1
            perfect_bonus = 25
            self.player_chips += perfect_bonus
            print(f"{Colors.MAGENTA}🏆 Perfect game bonus: +{perfect_bonus} chips!{Colors.END}")
        
        # Show mini stats
        print(f"\n{Colors.CYAN}📊 Win Rate: {self.stats.win_rate():.1f}% | Enemies Defeated: {self.stats.enemies_defeated}{Colors.END}")
        
        time.sleep(3)
        self.perfect_game_tracker = True  # Reset for next level
    
    def create_enemy(self) -> Enemy:
        enemy_types = [
            ("Bandit", 1), ("Rogue", 2), ("Mercenary", 3), ("Assassin", 4), 
            ("Warlord", 5), ("Shadow", 6), ("Vampire", 7), ("Demon", 8), 
            ("Dragon", 9), ("Lich", 10)
        ]
        
        # Select enemy type based on level
        enemy_type = "Bandit"
        for enemy_name, min_level in enemy_types:
            if self.level >= min_level:
                enemy_type = enemy_name
        
        # Difficulty scaling
        difficulty_multipliers = {
            "easy": 0.8,
            "normal": 1.0,
            "hard": 1.3,
            "nightmare": 1.6
        }
        multiplier = difficulty_multipliers.get(self.difficulty, 1.0)
        
        name = f"{enemy_type} Lv.{self.level}"
        enemy = Enemy(name, self.level)
        enemy.chips = int(enemy.chips * multiplier)
        enemy.aggression *= multiplier
        
        return enemy
    
    def game_over_screen(self, enemy_name):
        self.save_high_score()
        
        game_over = f"""
{Colors.RED + Colors.BOLD}
    ╔══════════════════════════════════════╗
    ║              💀 GAME OVER 💀          ║
    ║                                      ║
    ║     You were defeated by             ║
    ║        {enemy_name:<20}        ║
    ║                                      ║
    ║     Final Level: {self.level:<2d}               ║
    ║     Difficulty: {self.difficulty.title():<10}        ║
    ║     Victories: {self.victories:<2d}                 ║
    ║     Win Rate: {self.stats.win_rate():<4.1f}%            ║
    ╚══════════════════════════════════════╝
{Colors.END}"""
        clear_screen()
        print(game_over)
        
        if self.level > self.high_score:
            animated_text("🎉 NEW HIGH SCORE! 🎉", Colors.YELLOW + Colors.BOLD)
        
        self.show_final_stats()
        time.sleep(3)
    
    def show_final_stats(self):
        print(f"\n{Colors.CYAN + Colors.BOLD}📊 FINAL STATISTICS{Colors.END}")
        print(f"┌{'─' * 30}┐")
        print(f"│ Hands played: {self.stats.hands_played:<13} │")
        print(f"│ Hands won: {self.stats.hands_won:<16} │")
        print(f"│ Win rate: {self.stats.win_rate():<17.1f}% │")
        print(f"│ Enemies defeated: {self.stats.enemies_defeated:<9} │")
        print(f"│ Total chips won: {self.stats.total_chips_won:<10,} │")
        if self.stats.best_hand:
            print(f"│ Best hand: {self.stats.best_hand.rank.name.replace('_', ' ').title():<15} │")
        print(f"│ Lucky escapes: {self.stats.lucky_escapes:<12} │")
        print(f"│ Perfect games: {self.stats.perfect_games:<12} │")
        print(f"└{'─' * 30}┘")
    
    def victory_screen(self):
        self.save_high_score()
        
        victory = f"""
{Colors.MAGENTA + Colors.BOLD}
    ✨🏆✨🏆✨🏆✨🏆✨🏆✨🏆✨🏆✨
    🏆                                 🏆
    ✨    🎉 CONGRATULATIONS! 🎉       ✨
    🏆                                 🏆
    ✨   You conquered the realm!      ✨
    🏆   Difficulty: {self.difficulty.title():<15}     🏆
    ✨   Final Chips: {self.player_chips:<12,}    ✨
    🏆   Master of Poker achieved!     🏆
    ✨🏆✨🏆✨🏆✨🏆✨🏆✨🏆✨🏆✨
{Colors.END}"""
        clear_screen()
        print(victory)
        
        # Ultimate victory bonus
        ultimate_bonus = 500 * (1 if self.difficulty == "easy" else 2 if self.difficulty == "normal" else 3 if self.difficulty == "hard" else 5)
        self.player_chips += ultimate_bonus
        animated_text(f"🎆 Ultimate Victory Bonus: +{ultimate_bonus:,} chips!", Colors.YELLOW + Colors.BOLD)
        
        self.show_final_stats()
        time.sleep(5)
    
    def main_menu(self):
        while True:
            clear_screen()
            display_title()
            
            if hasattr(self, 'high_score') and self.high_score > 0:
                print(f"{Colors.YELLOW}🏆 High Score: Level {self.high_score}{Colors.END}")
            
            print(f"\n{Colors.BOLD}🎮 MAIN MENU{Colors.END}")
            print(f"1. {Colors.GREEN}Start New Game{Colors.END}")
            print(f"2. {Colors.CYAN}View Statistics{Colors.END}")
            print(f"3. {Colors.YELLOW}How to Play{Colors.END}")
            print(f"4. {Colors.RED}Quit{Colors.END}")
            
            choice = input(f"\n{Colors.CYAN}Choose option (1-4): {Colors.END}").strip()
            
            if choice == "1":
                self.difficulty_selection()
                self.play()
                return
            elif choice == "2":
                self.show_stats()
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            elif choice == "3":
                self.show_tutorial()
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            elif choice == "4":
                animated_text("Thanks for playing! 🎴", Colors.YELLOW)
                return
            else:
                animated_text("❌ Invalid choice!", Colors.RED)
                time.sleep(1)
    
    def show_tutorial(self):
        clear_screen()
        tutorial = f"""
{Colors.CYAN + Colors.BOLD}
╔═══════════════════════════════════════════════════╗
║                  🎓 HOW TO PLAY                   ║
╚═══════════════════════════════════════════════════╝
{Colors.END}

{Colors.YELLOW}🎯 OBJECTIVE:{Colors.END}
Battle through 10 levels of enemies using Texas Hold'em poker!

{Colors.YELLOW}🃏 GAMEPLAY:{Colors.END}
• You start with chips based on difficulty
• Each enemy has their own chip stack and abilities
• Play standard Texas Hold'em (2 hole cards + 5 community cards)
• Beat the enemy to advance to the next level
• Lose all chips = GAME OVER (permadeath!)

{Colors.YELLOW}💰 BETTING ACTIONS:{Colors.END}
• CHECK: Pass without betting (when no bet to call)
• BET/RAISE: Increase the stakes
• CALL: Match opponent's bet
• FOLD: Give up the hand

{Colors.YELLOW}🎁 ITEMS & BONUSES:{Colors.END}
• Find items after winning hands (30% chance)
• Items provide luck boosts, chips, or healing
• Level up bonuses scale with difficulty
• Perfect games (no losses) grant extra rewards

{Colors.YELLOW}⚔️ ENEMY ABILITIES:{Colors.END}
• Higher level enemies have special abilities
• They play more aggressively and bluff more
• Dragon and Lich have devastating powers!

{Colors.YELLOW}🏆 DIFFICULTY MODES:{Colors.END}
• Easy: 150 chips, weaker enemies, 1x rewards
• Normal: 100 chips, balanced, 1.2x rewards  
• Hard: 75 chips, stronger enemies, 1.5x rewards
• Nightmare: 50 chips, brutal enemies, 2x rewards

{Colors.RED + Colors.BOLD}⚠️  ONE LIFE ONLY - No saves, no continues! ⚠️{Colors.END}
        """
        
        print(tutorial)
    
    def play(self):
        clear_screen()
        display_title()
        
        intro_text = f"""
{Colors.CYAN}
🎯 Welcome, brave poker warrior!
   
   Battle through 10 levels of increasingly dangerous foes!
   Difficulty: {Colors.BOLD}{self.difficulty.title()}{Colors.END}{Colors.CYAN}
   Starting chips: {Colors.BOLD}{self.player_chips:,}{Colors.END}{Colors.CYAN}
   
   Each victory grants you power and riches...
   But one defeat means PERMADEATH! ⚰️
   
   May the cards be ever in your favor! 🍀
{Colors.END}"""
        
        slow_print(intro_text, 0.02)
        input(f"\n{Colors.BOLD}Press Enter to begin your journey...{Colors.END}")
        
        self.perfect_game_tracker = True
        
        while self.player_chips > 0:
            enemy = self.create_enemy()
            
            # Enemy encounter
            encounter_text = f"""
{Colors.RED + Colors.BOLD}
    ⚔️  ENEMY ENCOUNTER! ⚔️
    
    A wild {enemy.name} appears!
    Enemy Power: {enemy.chips} chips
    Difficulty: {self.difficulty.title()}
{Colors.END}"""
            
            if enemy.special_ability:
                encounter_text += f"\n{Colors.MAGENTA}🔮 Special Ability: {enemy.special_ability}{Colors.END}"
            
            clear_screen()
            print(encounter_text)
            enemy_art = enemy.get_ascii_art()
            for line in enemy_art:
                print(f"    {line}")
            
            time.sleep(2)
            
            # Battle until someone runs out of chips
            enemy_hands_won = 0
            while self.player_chips > 0 and enemy.chips > 0:
                won = self.play_hand(enemy)
                
                if not won:
                    enemy_hands_won += 1
                    self.perfect_game_tracker = False
                
                if self.player_chips <= 0:
                    break
                
                if enemy.chips <= 0:
                    break
                
                input(f"\n{Colors.CYAN}Press Enter for next hand...{Colors.END}")
            
            if self.player_chips <= 0:
                self.game_over_screen(enemy.name)
                break
            else:
                animated_text(f"🎉 You defeated {enemy.name}!", Colors.GREEN)
                time.sleep(1)
                self.level_up()
                
                if self.level > 10:
                    self.victory_screen()
                    break
                
                continue_prompt = input(f"{Colors.CYAN}Continue to next level? (y/n): {Colors.END}").lower()
                if continue_prompt != 'y':
                    print(f"{Colors.BOLD}Thanks for playing! Final level: {self.level}{Colors.END}")
                    self.save_high_score()
                    break

if __name__ == "__main__":
    try:
        game = RoguelikePoker()
        game.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Game interrupted. Thanks for playing!{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.END}")
        import traceback
        traceback.print_exc()