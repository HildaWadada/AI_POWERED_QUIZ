import json
import os
from typing import Any

import openai
import yaml
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self, prompts_path: str = "prompts.yaml") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        openai.api_key = api_key
        self.prompts = self._load_prompts(prompts_path)  # <-- now works

    # ------------------- Load Prompts -------------------
    def _load_prompts(self, path: str) -> dict[str, str]:
        """Load prompts from YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompts file not found: {path}")

        with open(path, encoding="utf-8") as file:
            return yaml.safe_load(file)

    # ------------------- Chat Completion -------------------
    def _chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 600,
    ) -> str:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    # ------------------- Question Generation -------------------
    def generate_questions(self, topic: str) -> list[dict[str, Any]]:
        user_prompt = self.prompts["generate_questions"].format(topic=topic)

        content = self._chat_completion(
            system_prompt=self.prompts["system"],
            user_prompt=user_prompt,
        )

        try:
            start = content.find("[")
            end = content.rfind("]") + 1
            return json.loads(content[start:end])
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON returned from LLM") from exc

    # ------------------- Freeform Evaluation -------------------
    def evaluate_freeform(
        self,
        *,
        question: str,
        correct_answer: str,
        user_answer: str,
    ) -> bool:
        user_prompt = self.prompts["evaluate_freeform"].format(
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
        )

        result = self._chat_completion(
            system_prompt=self.prompts["system"],
            user_prompt=user_prompt,
            temperature=0,
            max_tokens=10,
        )

        return result.lower() == "correct"

    # ------------------- Explanation -------------------
    def explain_mistake(
        self,
        *,
        question: str,
        correct_answer: str,
        user_answer: str,
    ) -> str:
        user_prompt = self.prompts["explain_mistake"].format(
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
        )

        return self._chat_completion(
            system_prompt=self.prompts["system"],
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=120,
        )
