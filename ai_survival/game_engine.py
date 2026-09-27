import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Scenario:
    description: str
    actions: Dict[int, str]
    correct_actions: List[int]
    success_msg: str
    fail_msg: str


DEFAULT_SCENARIOS = [
    Scenario(
        description="A low rolling boulder is speeding towards you on the narrow track!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[1],
        success_msg="You leaped cleanly over the boulder as it smashed into the ground below!",
        fail_msg="The boulder struck you hard before you could get out of the way!"
    ),
    Scenario(
        description="A massive stalactite detaches from above and plunges downward!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[2, 3],
        success_msg="You quickly side-stepped and watched the massive rock crash right where you stood!",
        fail_msg="You couldn't escape the blast radius of the falling debris!"
    ),
    Scenario(
        description="A wall of low-lying plasma energy surges across the floor!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[1],
        success_msg="You jumped gracefully over the plasma surge as it crackled underneath!",
        fail_msg="The energy surge caught your feet, inflicting heavy shock damage!"
    ),
    Scenario(
        description="A collapsed timber beams gate blocks the center path!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[2, 3],
        success_msg="You swiftly skirted around the side of the collapsed obstacle!",
        fail_msg="You slammed straight into the heavy wooden beams!"
    ),
    Scenario(
        description="A dense swarm of razor-horn insects swoops down at chest height!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[4],
        success_msg="You crouched and charged forward beneath the flying swarm safely!",
        fail_msg="You jumped or stepped sideways right into the dense swarm!"
    ),
    Scenario(
        description="A sudden floor fissure splits open right under your feet!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[1],
        success_msg="With a powerful leap, you cleared the opening chasm!",
        fail_msg="You tumbled into the fissure, suffering a severe drop!"
    ),
    Scenario(
        description="A runaway spiked steam roller sweeps down the left lane!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[3],
        success_msg="You veered right into the open lane as the steam roller thundered past on your left!",
        fail_msg="You failed to move right into safety!"
    ),
    Scenario(
        description="An electrified fence blocks the right side of the corridor!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[2],
        success_msg="You dodged left away from the crackling high-voltage grid!",
        fail_msg="You stepped towards or into the high-voltage fence!"
    ),
    Scenario(
        description="A high overhead swinging iron pendulum sweeps above the track!",
        actions={1: "Jump", 2: "Move Left", 3: "Move Right", 4: "Continue"},
        correct_actions=[4],
        success_msg="You sprinted forward beneath the arc of the swinging pendulum without jumping!",
        fail_msg="Jumping or veering sideways brought you directly into the pendulum's path!"
    ),
]


TARGET_SCORE = 500


class GameState:
    def __init__(self, initial_lives: int = 3):
        self.lives = initial_lives
        self.score = 0
        self.turn = 1
        self.game_over = False

    def is_alive(self) -> bool:
        return self.lives > 0 and self.score < TARGET_SCORE

    def reached_target(self) -> bool:
        return self.score >= TARGET_SCORE


class GameEngine:
    def __init__(self, scenarios: List[Scenario] = None):
        self.scenarios = scenarios or DEFAULT_SCENARIOS
        self.state = GameState()
        self.current_scenario: Scenario = None

    def start_game(self):
        self.state = GameState()
        self.next_turn()

    def next_turn(self) -> Scenario:
        if not self.state.is_alive():
            self.state.game_over = True
            return None
        self.current_scenario = random.choice(self.scenarios)
        return self.current_scenario

    def process_action(self, action_id: int) -> Tuple[bool, str]:
        """
        Processes player action choice (1-4).
        Returns (success: bool, message: str).
        """
        if self.state.game_over or not self.current_scenario:
            return False, "Game is over."

        action_name = self.current_scenario.actions.get(action_id, "Unknown Action")

        if action_id in self.current_scenario.correct_actions:
            self.state.score += 10
            msg = f"Action: {action_name}\n\nResult: {self.current_scenario.success_msg}"
            success = True
        else:
            self.state.lives -= 1
            msg = f"Action: {action_name}\n\nResult: {self.current_scenario.fail_msg}"
            success = False

        if not self.state.is_alive():
            self.state.game_over = True

        self.state.turn += 1
        return success, msg
