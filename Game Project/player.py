class Player:
    def __init__(self,name):
        self.name = name
        self.health = 100
        self.max_health = 200
        self.inventory = {
            "Health Potion": 3,  # Quantity of each item
            "Time Bomb": 1,
            "Temporal Shield": 2
        }
        self.score = 0
        self.artifacts = 0
        self.max_artifacts = 3

    def use_item(self, item_name):
        """Uses an item from the inventory."""
        if self.inventory.get(item_name, 0) > 0:
            self.inventory[item_name] -= 1
            if item_name == "Health Potion":
                self.health = min(self.max_health, self.health + 20)
                return f"You used a Health Potion! (+20 health)"
            elif item_name == "Time Bomb":
                return f"You used a Time Bomb! It deals massive damage!"
            elif item_name == "Temporal Shield":
                return f"You used a Temporal Shield! Damage resistance increased!"
            return True
        return False

    def add_item(self, item_name, quantity=1):
        """Adds an item to the inventory."""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity