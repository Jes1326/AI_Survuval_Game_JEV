from laya import Router

# Load the model
router = Router(preload=True)

def respond(lost_something):
    if lost_something == "yes":
        print("You can find the lost items at the lost and found department.")
    elif lost_something == "no":
        print("You have not lost anything.")
    else:
        print("Please clarify whether you have lost something.")


def ask():
    while True:
        user_input = input("Have you lost anything? (yes/no): ").strip().lower()

        state = {
            "body": user_input
        }

        questions = {
            "action": {
                "type": "choice",
                "instructions": (
                    "Classify the user's response as yes, no, "
                    "or uncertain."
                ),
                "criteria": {
                    "yes": "The user confirms they have lost something.",
                    "no": "The user confirms they have not lost anything.",
                    "uncertain": "The response is unclear or expresses uncertainty."
                }
            }
        }

        result = router.predict(state, questions)

        lost_something = result["answers"]["action"]["choice"]

        print(f"Choice: {lost_something}")

        if lost_something in ("yes", "no"):
            respond(lost_something)
            return lost_something

        print("I'm not sure I understood. Please try again.")


def main():
    lost_something = ask()


if __name__ == "__main__":
    main()