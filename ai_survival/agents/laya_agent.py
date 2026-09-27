import os
import time

# Suppress Hugging Face Hub progress bars and symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

_LAYA_ROUTER = None
_LAYA_INITIALIZED = False


def get_laya_router():
    global _LAYA_ROUTER, _LAYA_INITIALIZED
    if not _LAYA_INITIALIZED:
        _LAYA_INITIALIZED = True
        try:
            print("\n[Laya Agent] Loading local PyTorch model weights (first time only)...")
            from laya import Router
            _LAYA_ROUTER = Router(preload=True)
            print("[Laya Agent] Model loaded successfully!\n")
        except Exception as e:
            _LAYA_ROUTER = None
            print(f"[Laya Agent Warning]: Failed to initialize local Laya router ({e})")
    return _LAYA_ROUTER


def get_laya_decision(scenario_description: str, actions: dict) -> tuple[int, float]:
    """
    Uses local Laya model to evaluate scenario and select optimal action (1-4).
    Returns (action_id: int, latency_ms: float).
    """
    router = get_laya_router()
    if router is None:
        return 1, 0.0

    action_map = {
        1: "jump",
        2: "left",
        3: "right",
        4: "continue"
    }
    
    rev_action_map = {v: k for k, v in action_map.items()}

    state = {
        "body": scenario_description
    }

    questions = {
        "action": {
            "type": "choice",
            "instructions": "Choose the safest action to avoid the obstacle.",
            "criteria": {
                "jump": "Jump over low rolling obstacles or floor fissures.",
                "left": "Move to the left lane to avoid right or center blockades.",
                "right": "Move to the right lane to avoid left or center blockades.",
                "continue": "Continue forward without changing position or ducking under high hazards."
            }
        }
    }

    start_time = time.perf_counter()
    action_id = 1

    try:
        result = _LAYA_ROUTER.predict(state, questions)
        # Parse prediction answer
        chosen_key = None
        if isinstance(result, dict):
            action_res = result.get("action", {})
            if isinstance(action_res, dict):
                chosen_key = action_res.get("choice") or action_res.get("prediction")
            elif isinstance(action_res, str):
                chosen_key = action_res
        
        if chosen_key in rev_action_map:
            action_id = rev_action_map[chosen_key]
        else:
            action_id = 1

    except Exception as e:
        print(f"[Laya Agent Error]: {e}")
        action_id = 1

    latency_ms = (time.perf_counter() - start_time) * 1000.0
    return action_id, latency_ms
