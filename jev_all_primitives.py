import time
import os
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Noul, Choice, Score

load_dotenv()

api_key = os.getenv("TYPESAFE_API_KEY")

client = TypeSafeClient(
    api_key=api_key,
    base_url="https://openrouter.ai/api",
)

def demo_primitives(user_input: str):
    print(f"\n==========================================")
    print(f" Input: '{user_input}'")
    print(f"==========================================")

    start_time = time.perf_counter()

    response = client.system_one(
        state=user_input,
        questions={
            # 1. NOUL: Probabilistic evaluation (0.0 to 1.0 confidence score)
            "is_item_lost": Noul(
                instructions="Is the user asking about a lost item or seeking lost and found?"
            ),

            # 2. CHOICE: Categorical selection among defined options with criteria mapping
            "category": Choice(
                instructions="Classify the type of item mentioned by the user.",
                criteria={
                    "electronics": "Phones, laptops, chargers, headphones, or gadgets",
                    "documents": "IDs, passports, wallets, keys, or official cards",
                    "apparel": "Clothing, bags, jackets, hats, or shoes",
                    "other": "Any other physical item or unspecified general query"
                }
            ),

            # 3. SCORE: Ordinal scale evaluation based on an ordered rubric list
            "urgency": Score(
                instructions="Rate the urgency level of this lost item inquiry.",
                criteria=[
                    "Low: General inquiry or checking without immediate distress",
                    "Medium: Recently lost item, asking for steps to retrieve",
                    "High: Critical lost item (e.g. passport, wallet, keys late at night)"
                ]
            )
        }
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(f"\n[Response Time / Latency]: {elapsed_ms:.2f} ms")

    # 1. Parse Noul Output
    noul_ans = response.answers["is_item_lost"]
    print(f"\n[1] NOUL (Probability Score):")
    print(f"    Confidence: {noul_ans.noul:.2f}")

    # 2. Parse Choice Output
    choice_ans = response.answers["category"]
    print(f"\n[2] CHOICE (Categorical Selection):")
    print(f"    Selected Category: '{choice_ans.choice}'")

    # 3. Parse Score Output
    score_ans = response.answers["urgency"]
    print(f"\n[3] SCORE (Rubric Rank Evaluation):")
    print(f"    Assigned Score Index: {score_ans.score} (0=Low, 1=Medium, 2=High)")

if __name__ == "__main__":
    sample_inputs = [
        "I dropped my passport and wallet near the main exit, please help quickly!",
        "Do you have a lost and found for forgotten blue jackets?",
    ]
    for sample in sample_inputs:
        demo_primitives(sample)
