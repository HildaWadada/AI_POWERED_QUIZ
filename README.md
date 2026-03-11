# Interactive Learning Tool (AI‑Powered Quiz Companion)

## Overview

The **Interactive Learning Tool** is a command‑line, AI‑powered learning companion designed to help users study programming topics through quizzes, tests, and guided feedback. It dynamically generates questions using a Large Language Model (LLM), evaluates both multiple‑choice and free‑form answers, tracks performance, and provides explanations to help users learn from mistakes.

## Key Features

*  Topic‑based quizzes (e.g., OOP, Python basics, data structures)
*  Quick Topic Quiz mode
*  Test Mode with configurable number of questions
*  AI‑generated questions and answer evaluation
*  Supports both MCQs and free‑form answers
*  Session summaries and result persistence
*  Object‑Oriented Design (OOP)

## Project Structure
project/
│
├── main.py                # Application entry point and menu handling
├── quiz_manager.py        # Orchestrates quiz flow and scoring
├── question.py            # Question model and behavior
├── llm_client.py          # Handles all LLM interactions
├── prompts.yml            # Centralized prompt definitions
├── results.txt            # Stored quiz results
│
├── tests/                 # Unit tests
│   └── test_*.py
│
├── requirements.txt       # Project dependencies
└── README.md

## Installation & Setup

### Prerequisites

* Python **3.10+**
* An OpenAI API key

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Configuration

Created a `.env` file in the project root:
OPENAI_API_KEY=

## Running the Application

Start the program by running:
```bash
python main.py
```

You will be presented with an interactive menu that allows you to:

* Generate a question
* View statistics
* Enter practice mode
* Enter test mode
* Manage questions
* Start a quick topic quiz
* History and stats
* Exit the application

## How It Works (High‑Level Flow)

1. **main.py** displays the menu and handles user input
2. User actions are delegated to **QuizManager**
3. **QuizManager** requests questions via **LLMClient**
4. Questions are represented as **Question** objects
5. Answers are evaluated and scored
6. Results are summarized and saved to `results.txt`

## Prompt Management

All AI prompts are stored in **`prompts.yml`**, separating AI behavior from application logic. This design:

* Improves maintainability
* Allows prompt updates without code changes
* Encourages prompt reuse across tasks

## Testing
Unit tests are located in the `tests/` directory.
Run tests using:

```bash
pytest
```
Each core class is tested to ensure correctness of quiz flow, scoring, and question handling.

## Code Quality & Tooling

* **Ruff** is used for linting and style enforcement
* Modular design ensures readability and maintainability



