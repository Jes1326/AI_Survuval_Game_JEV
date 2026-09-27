import sys
import time
import random
from .game_engine import GameEngine
from .agents import (
    get_jev_decision,
    get_laya_decision,
    get_llm_decision,
    PRESET_MODELS,
)

def print_header(state, mode_title="AI SURVIVAL"):
    print("\n" + "=" * 32)
    print(f"===== {mode_title} =====")
    print(f"Score: {state.score}")
    print(f"Lives: {state.lives}")
    print(f"Turn:  {state.turn}")
    print("=" * 32 + "\n")


def print_scoreboard(player_name: str, score: int, turns: int, total_time_sec: float, latencies: list):
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    status = "VICTORY (Reached 500 Pts!)" if score >= 500 else ("GAME OVER (Eliminated)" if score < 500 else "FINISHED")

    print("\n" + "╔" + "═" * 48 + "╗")
    print(f"║               SCOREBOARD ({player_name})             ║")
    print("╠" + "═" * 48 + "╣")
    print(f"║  Status:               {status:<23} ║")
    print(f"║  Final Score:          {score:<23} ║")
    print(f"║  Turns Completed:      {turns:<23} ║")
    print(f"║  Avg Decision Time:    {avg_latency:.2f} ms              ║")
    print(f"║  Total Time Taken:     {total_time_sec:.2f} s                  ║")
    print("╚" + "═" * 48 + "╝\n")


def run_manual_game():
    engine = GameEngine()
    engine.start_game()

    print("\n--- Manual Mode ---")
    print("Try to reach the target score of 500 points!\n")

    latencies = []
    start_time = time.perf_counter()

    while engine.state.is_alive():
        scenario = engine.next_turn()
        if not scenario:
            break

        print_header(engine.state, "MANUAL SURVIVAL")
        print(f"Scenario: {scenario.description}\n")

        for key, action_str in scenario.actions.items():
            print(f"{key}. {action_str}")

        print()

        chosen_action = None
        turn_start = time.perf_counter()
        while chosen_action not in scenario.actions:
            try:
                user_input = input("Choose your action (1-4, or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("\nGame exited by player.")
                    return
                chosen_action = int(user_input)
                if chosen_action not in scenario.actions:
                    print("Invalid choice. Please enter a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a valid number (1-4).")

        turn_latency = (time.perf_counter() - turn_start) * 1000.0
        latencies.append(turn_latency)

        success, result_msg = engine.process_action(chosen_action)
        print(f"\n{result_msg}")

    total_elapsed = time.perf_counter() - start_time
    print_scoreboard("Manual Player", engine.state.score, engine.state.turn - 1, total_elapsed, latencies)


def run_jev_game():
    engine = GameEngine()
    engine.start_game()

    print("\n--- Jev AI Mode ---")
    print("Watch Jev AI attempt to reach 500 points!\n")

    latencies = []
    start_time = time.perf_counter()

    while engine.state.is_alive():
        scenario = engine.next_turn()
        if not scenario:
            break

        print_header(engine.state, "JEV AI SURVIVAL")
        print(f"Scenario: {scenario.description}\n")

        for key, action_str in scenario.actions.items():
            print(f"{key}. {action_str}")

        print("\nJev is analyzing the scenario...")
        action_id, latency_ms = get_jev_decision(scenario.description, scenario.actions)
        latencies.append(latency_ms)

        print(f"Jev chose: {action_id}. {scenario.actions[action_id]} (⚡ {latency_ms:.2f} ms)")

        success, result_msg = engine.process_action(action_id)
        print(f"\n{result_msg}")
        time.sleep(1.0)

    total_elapsed = time.perf_counter() - start_time
    print_scoreboard("Jev AI", engine.state.score, engine.state.turn - 1, total_elapsed, latencies)


def run_laya_game():
    engine = GameEngine()
    engine.start_game()

    print("\n--- Laya AI Mode ---")
    print("Watch Laya local model attempt to reach 500 points!\n")

    latencies = []
    start_time = time.perf_counter()

    while engine.state.is_alive():
        scenario = engine.next_turn()
        if not scenario:
            break

        print_header(engine.state, "LAYA AI SURVIVAL")
        print(f"Scenario: {scenario.description}\n")

        for key, action_str in scenario.actions.items():
            print(f"{key}. {action_str}")

        print("\nLaya is analyzing the scenario...")
        action_id, latency_ms = get_laya_decision(scenario.description, scenario.actions)
        latencies.append(latency_ms)

        print(f"Laya chose: {action_id}. {scenario.actions[action_id]} (⚡ {latency_ms:.2f} ms)")

        success, result_msg = engine.process_action(action_id)
        print(f"\n{result_msg}")
        time.sleep(1.0)

    total_elapsed = time.perf_counter() - start_time
    print_scoreboard("Laya AI", engine.state.score, engine.state.turn - 1, total_elapsed, latencies)


def get_agent_decision_by_spec(agent_spec: tuple[str, str], scenario_desc: str, actions: dict) -> tuple[int, str, float]:
    agent_type, param = agent_spec
    if agent_type == "jev":
        act, lat = get_jev_decision(scenario_desc, actions)
        return act, "Selected optimal choice via TypeSafe SDK.", lat
    elif agent_type == "laya":
        act, lat = get_laya_decision(scenario_desc, actions)
        return act, "Selected optimal choice via local Laya model.", lat
    else:  # openrouter
        return get_llm_decision(scenario_desc, actions, model_name=param)


def select_competitor(prompt_title: str) -> tuple[str, tuple[str, str]]:
    """
    Returns (display_name, (agent_type, param))
    """
    print(f"\n{prompt_title}:")
    print("  1. Jev AI (TypeSafe SDK)")
    print("  2. Laya AI (Local HuggingFace Model)")
    idx = 3
    or_keys = {}
    for key, (name, model_id) in PRESET_MODELS.items():
        print(f"  {idx}. {name} ({model_id})")
        or_keys[str(idx)] = (name, model_id)
        idx += 1
    print(f"  {idx}. Custom OpenRouter Model ID")
    custom_key = str(idx)

    choice = input(f"\nChoice (1-{custom_key}): ").strip()

    if choice == "1":
        return "Jev AI", ("jev", "")
    elif choice == "2":
        return "Laya AI", ("laya", "")
    elif choice in or_keys:
        name, model_id = or_keys[choice]
        return name, ("openrouter", model_id)
    elif choice == custom_key:
        custom_id = input("Enter OpenRouter model ID: ").strip()
        if custom_id:
            return custom_id, ("openrouter", custom_id)

    return "Jev AI", ("jev", "")


def run_comparison_game():
    name1, spec1 = select_competitor("Select Competitor 1")
    name2, spec2 = select_competitor("Select Competitor 2")

    engine1 = GameEngine()
    engine2 = GameEngine()

    engine1.start_game()
    engine2.start_game()

    latencies1 = []
    latencies2 = []
    start_time1 = time.perf_counter()
    start_time2 = time.perf_counter()
    finish_time1 = None
    finish_time2 = None

    print("\n" + "=" * 55)
    print(f"--- MODEL COMPARISON: {name1} vs {name2} ---")
    print(f"Target Score: 500 points")
    print("=" * 55 + "\n")

    while engine1.state.is_alive() or engine2.state.is_alive():
        scenario = random.choice(engine1.scenarios)

        print("\n" + "░" * 55)
        print(f"ROUND {engine1.state.turn} | Scenario: {scenario.description}")
        print("░" * 55)

        # Competitor 1 Turn
        if engine1.state.is_alive():
            engine1.current_scenario = scenario
            print(f"\n🤖 [{name1} Turn]")
            action1, reason1, latency1 = get_agent_decision_by_spec(spec1, scenario.description, scenario.actions)
            latencies1.append(latency1)
            _, msg1 = engine1.process_action(action1)
            print(f"{name1} Chose: {action1}. {scenario.actions[action1]} (⏱️ {latency1:.2f} ms)")
            print(f"Reasoning: {reason1}")
            print(f"Result: {scenario.success_msg if action1 in scenario.correct_actions else scenario.fail_msg}")
            print(f"{name1} Status -> Score: {engine1.state.score}/500 | Lives: {engine1.state.lives}")
            if not engine1.state.is_alive() and finish_time1 is None:
                finish_time1 = time.perf_counter() - start_time1
        else:
            print(f"\n🤖 [{name1}] - GAME ENDED")

        # Competitor 2 Turn
        if engine2.state.is_alive():
            engine2.current_scenario = scenario
            print(f"\n🧠 [{name2} Turn]")
            action2, reason2, latency2 = get_agent_decision_by_spec(spec2, scenario.description, scenario.actions)
            latencies2.append(latency2)
            _, msg2 = engine2.process_action(action2)
            print(f"{name2} Chose: {action2}. {scenario.actions[action2]} (⏱️ {latency2:.2f} ms)")
            print(f"Reasoning: {reason2}")
            print(f"Result: {scenario.success_msg if action2 in scenario.correct_actions else scenario.fail_msg}")
            print(f"{name2} Status -> Score: {engine2.state.score}/500 | Lives: {engine2.state.lives}")
            if not engine2.state.is_alive() and finish_time2 is None:
                finish_time2 = time.perf_counter() - start_time2
        else:
            print(f"\n🧠 [{name2}] - GAME ENDED")

        time.sleep(1.0)

    if finish_time1 is None:
        finish_time1 = time.perf_counter() - start_time1
    if finish_time2 is None:
        finish_time2 = time.perf_counter() - start_time2

    print("\n" + "=" * 55)
    print("              FINAL COMPARISON SCOREBOARD              ")
    print("=" * 55)
    print_scoreboard(name1, engine1.state.score, engine1.state.turn - 1, finish_time1, latencies1)
    print_scoreboard(name2, engine2.state.score, engine2.state.turn - 1, finish_time2, latencies2)


def print_game_over(state, player_name="Player"):
    print("\n" + "=" * 32)
    print(f"      GAME OVER ({player_name})      ")
    print(f"Final Score:    {state.score}")
    print(f"Turns Survived: {state.turn - 1}")
    print("=" * 32 + "\n")


def main():
    print("=" * 38)
    print("     AI SURVIVAL GAME LAUNCHER     ")
    print("=" * 38)
    print("1. Manual Mode (You play)")
    print("2. Jev AI Mode (Jev plays)")
    print("3. Laya AI Mode (Local Laya model plays)")
    print("4. Model Comparison Mode (Select Any 2 Competitors)")
    print("5. Exit")
    print()

    choice = input("Select mode (1-5): ").strip()
    if choice == '1':
        run_manual_game()
    elif choice == '2':
        run_jev_game()
    elif choice == '3':
        run_laya_game()
    elif choice == '4':
        run_comparison_game()
    else:
        print("Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame exited by user. Goodbye!")
        sys.exit(0)
