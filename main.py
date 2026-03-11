from quiz_manager import QuizManager
from question import Question


def main_menu():
    qm = QuizManager()

    while True:
        print("\n Interactive Learning Tool ")
        print("1. Generate Questions")
        print("2. View Statistics")
        print("3. Practice Mode")
        print("4. Test Mode")
        print("5. Manage Questions (Enable/Disable/List)")
        print("6. Quick Topic Quiz")
        print("7. View History & Stats")
        print("8. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            generate_questions(qm)
        elif choice == "2":
            qm.show_statistics()
        elif choice == "3":
            qm.practice_mode()  # topic selection handled inside QuizManager
        elif choice == "4":
            qm.test_mode()  # number of questions prompted if not provided
        elif choice == "5":
            manage_questions(qm)
        elif choice == "6":
            quick_topic_quiz(qm)
        elif choice == "7":
            view_history(qm)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


# ------------------- Generate Questions -------------------
def generate_questions(qm: QuizManager):
    topic = input("Enter a topic: ").strip()
    if not topic:
        print("Topic cannot be empty.")
        return

    print(f"\n📚 Generating questions for topic: {topic} ...")
    llm_questions = qm.llm_client.generate_questions(topic)

    if not llm_questions:
        print(" No questions generated.")
        return

    for idx, qdata in enumerate(llm_questions, start=1):
        print(f"\nQuestion {idx}: {qdata['text']}")
        if qdata["qtype"] == "MCQ":
            print("Options:")
            for i, opt in enumerate(qdata["options"], start=1):
                print(f"{i}. {opt}")

        accept = input("Do you want to accept this question? (y/n): ").strip().lower()
        if accept == "y":
            q = Question(
                text=qdata["text"],
                qtype=qdata["qtype"],
                options=qdata.get("options"),
                answer=qdata.get("answer"),
                topic=topic,
                source="LLM"
            )
            qm.add_question(q)
            print("✅ Question saved.")
        else:
            print("Question skipped.")


# ------------------- Manage Questions -------------------
def manage_questions(qm: QuizManager):
    while True:
        print("\n=== Manage Questions ===")
        print("1. List all questions")
        print("2. Enable a question")
        print("3. Disable a question")
        print("4. Back to main menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            qm.list_questions()
        elif choice == "2":
            qid = input("Enter the Question ID to enable: ").strip()
            qm.enable_disable_question(qid, True)
        elif choice == "3":
            qid = input("Enter the Question ID to disable: ").strip()
            qm.enable_disable_question(qid, False)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")


# ------------------- Quick Topic Quiz -------------------
def quick_topic_quiz(qm: QuizManager):
    topics = qm.get_topics()
    if not topics:
        print(" No topics available.")


    print("\nAvailable topics:")
    for i, topic in enumerate(topics, start=1):
        print(f"{i}. {topic}")

    try:
        choice = int(input(f"Select a topic number (1-{len(topics)}): ").strip())
        if 1 <= choice <= len(topics):
            selected_topic = topics[choice - 1]
        else:
            print("Invalid selection. Returning to main menu.")
            return
    except ValueError:
        print("Invalid input. Returning to main menu.")
        return

    topic_questions = qm.get_questions_by_topic(selected_topic)
    if not topic_questions:
        print(f" No active questions for topic '{selected_topic}'.")
        return

    # Ask up to 5 questions or fewer if not enough in topic
    num_questions = min(5, len(topic_questions))
    print(f"\n Starting Quick Topic Quiz on '{selected_topic}' with {num_questions} questions...")

    # Save current active questions, temporarily override _active_questions
    original_questions = qm._active_questions
    qm._active_questions = lambda topic=None: topic_questions
    qm.test_mode(num_questions)
    # Restore original method
    qm._active_questions = original_questions


# ------------------- View History & Stats -------------------
def view_history(qm: QuizManager):
    try:
        with open(qm.results_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(" No results available yet.")
        return

    if not lines:
        print(" No results available yet.")
        return

    print("\n=== Quiz History & Scores ===")
    for line in lines:
        print(line)

    print("\n📊 Performance Summary by Topic:")
    topic_stats = {}
    for q in qm.questions:
        if q.times_shown > 0:
            topic_stats.setdefault(q.topic, {"shown": 0, "correct": 0})
            topic_stats[q.topic]["shown"] += q.times_shown
            topic_stats[q.topic]["correct"] += q.correct_count

    if not topic_stats:
        print("No topic statistics available.")
        return

    for topic, stats in topic_stats.items():
        correct_pct = (stats["correct"] / stats["shown"] * 100) if stats["shown"] else 0
        print(f"{topic}: {stats['correct']}/{stats['shown']} correct ({correct_pct:.1f}%)")


# if __name__ == "__main__":
main_menu()
