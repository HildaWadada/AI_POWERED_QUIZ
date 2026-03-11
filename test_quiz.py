import unittest
import os
from question import Question
from quiz_manager import QuizManager

class TestQuizManager(unittest.TestCase):

    # 1. MCQ Evaluation Test
    def test_mcq_evaluation(self):
        q = Question(
            text="Which is a Python data type?",
            qtype="MCQ",
            options=["String", "Dog", "Car"],
            answer="String"
        )
        # Simulate correct answer
        user_answer = "String"
        correct = user_answer == q.answer
        self.assertTrue(correct)

        # Simulate wrong answer
        user_answer = "Dog"
        correct = user_answer == q.answer
        self.assertFalse(correct)

    # 2. Freeform Stats Update Test
    def test_mark_answer(self):
        q = Question(text="What is Python?", qtype="Freeform", answer="Programming language")
        q.mark_answer(True)
        q.mark_answer(False)
        self.assertEqual(q.times_shown, 2)
        self.assertEqual(q.correct_count, 1)
        self.assertEqual(q.incorrect_count, 1)

    # 3. Save/Load Questions Test
    def test_save_load_questions(self):
        qm = QuizManager(questions_file="test_questions.json")
        # Clear file first
        if os.path.exists("test_questions.json"):
            os.remove("test_questions.json")
        q = Question(text="Q1", qtype="Freeform", answer="A1")
        qm.add_question(q)

        # Reload manager to see if question persists
        qm2 = QuizManager(questions_file="test_questions.json")
        self.assertEqual(len(qm2.questions), 1)
        self.assertEqual(qm2.questions[0].text, "Q1")
        self.assertEqual(qm2.questions[0].answer, "A1")

        # Clean up test file
        os.remove("test_questions.json")

if __name__ == "__main__":
    unittest.main()
