import sys
import random
from pathlib import Path

# Add project root to sys.path so imports work regardless of execution location
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ai_survival.game_engine import GameEngine
    from ai_survival.agents import get_jev_decision, get_laya_decision, get_llm_decision, PRESET_MODELS
except ImportError:
    from game_engine import GameEngine
    from agents import get_jev_decision, get_laya_decision, get_llm_decision, PRESET_MODELS


def run_automated_suite():
    print("=" * 60)
    print("      AUTOMATED BENCHMARK SUITE: JEV vs OPENROUTER LLMs      ")
    print("=" * 60)

    # 1. Jev Solo Run
    print("\n--- RUN 1: JEV AI SOLO MODE ---")
    engine = GameEngine()
    engine.start_game()
    while engine.state.is_alive() and engine.state.turn <= 20:
        s = engine.current_scenario
        action, latency = get_jev_decision(s.description, s.actions)
        success, msg = engine.process_action(action)
        status = "SUCCESS" if success else "FAILED"
        print(f"Turn {engine.state.turn}: Scenario='{s.description[:40]}...' | Jev Chose {action} ({s.actions[action]}) [{latency:.1f}ms] -> {status} (Lives: {engine.state.lives}, Score: {engine.state.score})")
        engine.next_turn()
    print(f"JEV SOLO ENDED: Total Turns Survived = {engine.state.turn - 1}, Final Score = {engine.state.score}")

    # 2. Comparisons with LLMs (Models 1 to 3)
    models_to_test = ["1", "2", "3"]

    for idx, model_key in enumerate(models_to_test, 2):
        model_name, model_id = PRESET_MODELS[model_key]
        print(f"\n--- RUN {idx}: JEV AI vs {model_name} ({model_id}) ---")
        
        engine_jev = GameEngine()
        engine_other = GameEngine()
        engine_jev.start_game()
        engine_other.start_game()

        random.seed(42 + idx)

        turn = 1
        while (engine_jev.state.is_alive() or engine_other.state.is_alive()) and turn <= 10:
            scenario = random.choice(engine_jev.scenarios)
            print(f"\n[Round {turn}] Obstacle: {scenario.description}")
            
            # Jev turn
            if engine_jev.state.is_alive():
                engine_jev.current_scenario = scenario
                act_j, lat_j = get_jev_decision(scenario.description, scenario.actions)
                succ_j, _ = engine_jev.process_action(act_j)
                print(f"  [Jev AI]: Action {act_j} ({scenario.actions[act_j]}) | Succ: {succ_j} | Lives left: {engine_jev.state.lives} | Latency: {lat_j:.1f}ms")
            
            # Opponent turn
            if engine_other.state.is_alive():
                engine_other.current_scenario = scenario
                act_o, reason_o, lat_o = get_llm_decision(scenario.description, scenario.actions, model_name=model_id)
                succ_o, _ = engine_other.process_action(act_o)
                print(f"  [{model_name}]: Action {act_o} ({scenario.actions[act_o]}) | Succ: {succ_o} | Lives left: {engine_other.state.lives} | Latency: {lat_o:.1f}ms")
                print(f"     Reasoning: {reason_o}")

            turn += 1

        print(f"\nRESULTS: Jev Score: {engine_jev.state.score} vs {model_name} Score: {engine_other.state.score}")
        if engine_jev.state.score > engine_other.state.score:
            print(f"Winner: Jev AI")
        elif engine_other.state.score > engine_jev.state.score:
            print(f"Winner: {model_name}")
        else:
            print("Result: TIE")


if __name__ == "__main__":
    run_automated_suite()
