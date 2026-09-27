import os
import time
from pathlib import Path
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice

# Load .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

api_key = os.getenv("TYPESAFE_API_KEY")

client = TypeSafeClient(
    api_key=api_key,
    base_url="https://openrouter.ai/api",
)


def get_jev_decision(scenario_description: str, actions: dict) -> tuple[int, float]:
    """
    Uses Jev AI (TypeSafeClient Choice primitive) to select optimal action (1-4).
    Returns (action_id: int, latency_ms: float).
    """
    ACTION_DESCRIPTIONS = {
        "Jump": "Jump cleanly into the air. Best for low rolling obstacles, energy surges on the ground, or floor fissures.",
        "Move Left": "Side-step sharply to the left. Best for falling overhead objects or center path blockades.",
        "Move Right": "Side-step sharply to the right. Best for falling overhead objects or center path blockades.",
        "Continue": "Maintain pace forward. Best when ducking/staying low for flying swarms or high overhead hazards."
    }

    criteria = {
        str(key): f"{action_name}: {ACTION_DESCRIPTIONS.get(action_name, 'Action choice to navigate obstacles')}"
        for key, action_name in actions.items()
    }

    start_time = time.perf_counter()
    action_id = 1

    try:
        response = client.system_one(
            state=f"Obstacle Situation: {scenario_description}",
            questions={
                "selected_action": Choice(
                    instructions="Select the best and safest action to survive and avoid the obstacle.",
                    criteria=criteria
                )
            }
        )

        selected_choice = response.answers["selected_action"].choice
        action_id = int(selected_choice)
        if action_id not in actions:
            action_id = 1
    except Exception as e:
        print(f"[Jev AI Error]: {e}")
        action_id = 1

    latency_ms = (time.perf_counter() - start_time) * 1000.0
    return action_id, latency_ms
