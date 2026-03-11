import json
import random
from datetime import datetime
from typing import Optional

from llm_client import LLMClient
from question import Question


class QuizManager:
    def __init__(
        self,
        questions_file: str = "questions.json",
        results_file: str = "results.txt",
    ) -> None:
        self.questions_file = questions_file
        self.results_file = results_file
        self.questions = self._load_questions()
        self.llm_client = LLMClient()

        if not self.questions:
            self._save_questions()

    # ------------------- Persistence -------------------

    def _load_questions(self) -> list[Question]:
        try:
            with open(self.questions_file, encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []

        return [Question.from_dict(item) for item in data]

    def _save_questions(self) -> None:
        with open(self.questions_file, "w", encoding="utf-8") as file:
            json.dump(
                [q.to_dict() for q in self.questions],
                file,
                indent=4,
            )

    # ------------------- Add/Enable/Disable -------------------

    def add_question(self, question: Question) -> None:
        self.questions.append(question)
        self._save_questions()

    def enable_disable_question(self, qid: str, enable: bool) -> None:
        found = False
        for q in self.questions:
            if q.qid == qid:
                q.enabled = enable
                found = True
                break
        if found:
            self._save_questions()
            print(f"Question '{qid}' {'enabled' if enable else 'disabled'}.")
        else:
            print(f"Question ID '{qid}' not found.")

    def list_questions(self) -> None:
        if not self.questions:
            print(" No questions available.")
            return
        print("\n=== All Questions ===")
        for q in self.questions:
            status = "Enabled" if q.enabled else "Disabled"
            print(f"{q.qid} | {q.topic} | {status} | {q.qtype}")

    def get_topics(self) -> list[str]:
        topics = {q.topic for q in self.questions if q.enabled}
        return sorted(list(topics))

    def get_questions_by_topic(self, topic: str) -> list[Question]:
        return [q for q in self.questions if q.enabled and q.topic == topic]

    # ------------------- Helpers -------------------

    def _active_questions(self, topic: Optional[str] = None) -> list[Question]:
        questions = [q for q in self.questions if q.enabled]
        if topic:
            questions = [q for q in questions if q.topic == topic]
        return questions

    def _weighted_choice(self, questions: list[Question]) -> Question:
        weights = [
            1.0 if q.times_shown == 0 else 1.1 - (q.correct_count / q.times_shown)
            for q in questions
        ]
        return random.choices(questions, weights=weights, k=1)[0]

    # ------------------- Practice Mode -------------------

    def practice_mode(self) -> None:
        topics = self.get_topics()
        if not topics:
            print(" No active questions available.")
            return

        print("\nAvailable topics:")
        for i, topic in enumerate(topics, start=1):
            print(f"{i}. {topic}")
        print(f"{len(topics)+1}. All topics")

        try:
            choice = int(input(f"Select a topic (1-{len(topics)+1}): ").strip())
            if 1 <= choice <= len(topics):
                selected_topic = topics[choice-1]
            elif choice == len(topics)+1:
                selected_topic = None  # all topics
            else:
                print("Invalid choice. Exiting practice mode.")
                return
        except ValueError:
            print("Invalid input. Exiting practice mode.")
            return

        questions = self._active_questions(selected_topic)
        asked_ids: set[str] = set()
        session_correct = 0

        print("\n Practice Mode (press Enter to exit)\n")
        while True:
            unanswered = [q for q in questions if q.qid not in asked_ids]
            if not unanswered:
                print("\n Practice session complete!")
                break

            question = self._weighted_choice(unanswered)
            asked_ids.add(question.qid)
            question.times_shown += 1

            print(f"\n {question.text}")

            if question.qtype == "MCQ":
                for index, option in enumerate(question.options, start=1):
                    print(f"{index}. {option}")
                choice = input("Your answer: ").strip()
                if not choice:
                    break
                correct = ( 
                    choice.isdigit()
                    and question.options[int(choice)-1] == question.answer
                )
            else:
                user_answer = input("Your answer: ").strip()
                if not user_answer:
                    break
                correct = self.llm_client.evaluate_freeform(
                    question=question.text,
                    correct_answer=question.answer,
                    user_answer=user_answer,
                )

            question.mark_answer(correct)
            if correct:
                session_correct += 1
                print("✅ Correct!")
            else:
                print(f"❌ Incorrect. Answer: {question.answer}")

            self._save_questions()

        print(f"\nSession Results: {session_correct}/{len(asked_ids)} correct.")
        self._summarize_session(asked_ids, session_correct)

    # ------------------- Test Mode -------------------

    def test_mode(self, count: Optional[int] = None, topic: Optional[str] = None) -> None:
        questions = self._active_questions(topic)
        if not questions:
            print(" No active questions available.")
            return

        if count is None:
            while True:
                try:
                    count_input = input(f"Enter number of questions to answer (1-{len(questions)}): ").strip()
                    if not count_input:
                        print("Test cancelled.")
                        return
                    count = int(count_input)
                    if 1 <= count <= len(questions):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(questions)}.")
                except ValueError:
                    print("Please enter a valid number.")

        selected = random.sample(questions, min(count, len(questions)))
        score = 0
        asked_ids: set[str] = set()

        for index, question in enumerate(selected, start=1):
            asked_ids.add(question.qid)
            print(f"\nQuestion {index}: {question.text}")

            if question.qtype == "MCQ":
                for i, option in enumerate(question.options, start=1):
                    print(f"{i}. {option}")
                choice = input("Your answer: ").strip()
                correct = (
                    choice.isdigit()
                    and question.options[int(choice)-1] == question.answer
                )
            else:
                user_answer = input("Your answer: ").strip()
                correct = self.llm_client.evaluate_freeform(
                    question=question.text,
                    correct_answer=question.answer,
                    user_answer=user_answer,
                )

            question.mark_answer(correct)
            if correct:
                score += 1

        self._save_questions()
        self._log_result(score, len(selected))
        print(f"\n Test Results: {score}/{len(selected)} correct.")
        self._summarize_session(asked_ids, score)

    # ------------------- Reporting -------------------

    def _summarize_session(self, asked_ids: set[str], session_correct: int) -> None:
        print("\n📊 Session Summary")
        print(f"Questions attempted: {len(asked_ids)}")
        print(f"Correct answers: {session_correct}")

    def _log_result(self, score: int, total: int) -> None:
        with open(self.results_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.now()} | Score: {score}/{total}\n")

    def show_statistics(self) -> None:
        if not self.questions:
            print(" No questions available for statistics.")
            return

        print("\n📊 Statistics by Topic:")
        topic_stats = {}
        for q in self.questions:
            if q.times_shown > 0:
                topic_stats.setdefault(q.topic, {"shown": 0, "correct": 0})
                topic_stats[q.topic]["shown"] += q.times_shown
                topic_stats[q.topic]["correct"] += q.correct_count

        if not topic_stats:
            print("No statistics available yet. Answer some questions first!")
            return

        for topic, stats in topic_stats.items():
            shown = stats["shown"]
            correct = stats["correct"]
            pct = (correct / shown * 100) if shown else 0
            print(f"{topic}: {correct}/{shown} correct ({pct:.1f}%)")

    def view_history(self) -> None:
        try:
            with open(self.results_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(" No quiz history available yet.")
            return

        if not lines:
            print(" No quiz history available yet.")
            return

        print("\n=== Quiz History ===")
        for line in lines:
            print(line)
