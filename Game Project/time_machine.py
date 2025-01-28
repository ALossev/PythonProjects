from collections import deque
import random

class TimeMachine:
    """
    Handles time manipulation functionality, including saving game states,
    rewinding time, and triggering temporal anomalies.
    """
    def __init__(self):
        self.history = deque(maxlen=5)  # Stores last 5 game states
        self.rewinds_used = 0
        self.temporal_anomaly_cooldown = 3  # Triggers every 3 rooms

    def save_state(self, game_state):
        """Saves the current game state."""
        self.history.appendleft(game_state.copy())

    def rewind_time(self):
        """Restores the most recent saved state."""
        if self.history:
            self.rewinds_used += 1
            return self.history.popleft()
        return None

    def check_temporal_anomaly(self, player):
        """
        Triggers a random time-based event periodically.
        Returns True if an anomaly occurred.
        """
        self.temporal_anomaly_cooldown -= 1
        if self.temporal_anomaly_cooldown <= 0:
            self._trigger_anomaly(player)
            self.temporal_anomaly_cooldown = 3
            return True
        return False

    def _trigger_anomaly(self, player):
        """Internal method to execute a random temporal anomaly."""
        events = {
            1: ("Time shift! Your inventory shuffles!", 
                lambda: random.shuffle(list(player.inventory.keys()))),
            2: ("Age reversal! Health restored!", 
                lambda: setattr(player, 'health', player.max_health)),
            3: ("Temporal duplicate! Score doubled!", 
                lambda: setattr(player, 'score', player.score * 2)),
            4: ("Quantum entanglement! Enemy health halved in next combat!", 
                lambda: setattr(player, 'quantum_buff', True)),
        }
        event = random.choice(list(events.values()))
        print(f"\n*** TEMPORAL ANOMALY: {event[0]} ***")
        event[1]()