from typesafe_sdk import TypeSafeClient, Noul
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("TYPESAFE_API_KEY")

client = TypeSafeClient(
    api_key=api_key,
    base_url="https://openrouter.ai/api",
)

def respond(lost_something):
    if lost_something:
        print("You can find the loast items at the lost and found department.")
    else:
        print("You have not lost anything.")

def ask():
    while True:
        lost_something = input("Have you lost anything? (yes/no): ").lower()
        r=client.system_one(
            state=f"{lost_something}",
            questions={
                "lost_something": Noul(
                    instructions="Is the user's response affirmative or expressing uncertainty?"
                )
            }
        )
        if r.answers["lost_something"].noul > 0.7:
            lost_something = True
            print(f"score = {r.answers["lost_something"].noul}")
            print(respond(lost_something))
        elif r.answers["lost_something"].noul < 0.3:
            lost_something = False
            print(f"score = {r.answers["lost_something"].noul}")
            print(respond(lost_something))
        else:
            return ask()
    return lost_something   

def main():
    lost_something = ask()

if __name__ == "__main__":
    main()