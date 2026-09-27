import os
import json
import re
import time
import random
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

API_KEY = os.getenv("TYPESAFE_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PRESET_MODELS = {
    "1": ("DeepSeek Chat V3", "deepseek/deepseek-chat"),
    "2": ("Nemotron 3 Ultra", "nvidia/nemotron-3-ultra-550b-a55b:free"),
    "3": ("Meta Llama 3.3 70B", "meta-llama/llama-3.3-70b-instruct"),
}


def get_llm_decision(scenario_description: str, actions: dict, model_name: str = "deepseek/deepseek-chat", enable_reasoning: bool = True) -> tuple[int, str, float]:
    """
    Queries an OpenRouter chat model to evaluate scenario and select an action (1-4).
    Returns (action_id: int, explanation: str, latency_ms: float).
    """
    if not API_KEY:
        print("[OpenRouter Agent Warning] Missing TYPESAFE_API_KEY in environment.")
        return 1, "Fallback action due to missing API key.", 0.0

    prompt_actions = "\n".join([f"{k}: {v}" for k, v in actions.items()])
    user_prompt = (
        f"You are playing an endless survival action game.\n\n"
        f"Obstacle Scenario: {scenario_description}\n\n"
        f"Available Actions:\n{prompt_actions}\n\n"
        f"Which action is best to avoid the obstacle?\n"
        f"Reply ONLY with a JSON object containing:\n"
        f'- "action": an integer matching your choice (1, 2, 3, or 4)\n'
        f'- "reason": short 1-sentence reason for your action'
    )

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }

    if enable_reasoning:
        payload["reasoning"] = {"enabled": True}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    start_time = time.perf_counter()

    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=15)
            if response.status_code == 429 and attempt < max_retries:
                sleep_time = 3.0 * (attempt + 1)
                print(f"[OpenRouter Agent Info ({model_name})]: Rate limited (429). Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                continue

            response.raise_for_status()
            res_json = response.json()

            choice_obj = res_json.get("choices", [{}])[0]
            message_obj = choice_obj.get("message", {})
            content = message_obj.get("content", "")

            action_id = 1
            explanation = "Selected action based on scenario analysis."

            try:
                cleaned = re.sub(r"```(?:json)?", "", content).strip("` \n\r")
                parsed = json.loads(cleaned)
                action_id = int(parsed.get("action", 1))
                explanation = parsed.get("reason", explanation)
            except Exception:
                match = re.search(r'\b([1-4])\b', content)
                if match:
                    action_id = int(match.group(1))
                explanation = content.strip() if content else explanation

            if action_id not in actions:
                action_id = 1
            break

        except Exception as e:
            if attempt == max_retries:
                print(f"[OpenRouter Agent Error ({model_name})]: {e}")
                action_id = random.choice(list(actions.keys()))
                explanation = "Random fallback action due to connection or API error."

    latency_ms = (time.perf_counter() - start_time) * 1000.0
    return action_id, explanation, latency_ms
