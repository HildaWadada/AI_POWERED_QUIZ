import uuid

class Question:
    def __init__(self, text, qtype, options=None, answer=None, topic=None, source="LLM"):
        self.qid = str(uuid.uuid4())  # unique ID
        self.text = text
        self.qtype = qtype            # "MCQ" or "Freeform"
        self.options = options or []  # list of options if MCQ
        self.answer = answer          # correct answer
        self.topic = topic
        self.source = source          # "LLM" or "Manual"
        self.enabled = True
        self.times_shown = 0
        self.correct_count = 0
        self.incorrect_count = 0

    def mark_answer(self, correct: bool):
        self.times_shown += 1
        if correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1

    def to_dict(self):
        return {
            "qid": self.qid,
            "text": self.text,
            "qtype": self.qtype,
            "options": self.options,
            "answer": self.answer,
            "topic": self.topic,
            "source": self.source,
            "enabled": self.enabled,
            "times_shown": self.times_shown,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count
        }

    @staticmethod
    def from_dict(data):
        q = Question(
            text=data["text"],
            qtype=data["qtype"],
            options=data.get("options", []),
            answer=data.get("answer"),
            topic=data.get("topic"),
            source=data.get("source", "LLM")
        )
        q.qid = data["qid"]
        q.enabled = data.get("enabled", True)
        q.times_shown = data.get("times_shown", 0)
        q.correct_count = data.get("correct_count", 0)
        q.incorrect_count = data.get("incorrect_count", 0)
        return q
