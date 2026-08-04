# PawPal+ AI Dog Care Guide

## Title and Summary

PawPal+ is a hybrid Python application that combines the original Module 1-3 pet-care scheduler with a dog-only AI care assistant. The app helps dog owners manage schedules and answer routine care questions using local evidence plus a live OpenAI Responses API call.

This project matters because it pairs dependable scheduling logic with a grounded AI assistant, giving users quick, source-backed guidance while keeping medical and emergency decisions outside the system.

## Original Project

The original project was **PawPal+ from CodePath Modules 1-3**, an object-oriented pet-care scheduling application. Its original goals were to model owners, pets, tasks, time windows, and daily plans in Python and generate prioritized, conflict-aware recurring care schedules for pets.

This final project extends that scheduler with a retrieval-augmented AI dog-care guide. The original scheduling classes remain the reliable rule-based layer, while the new AI feature supports everyday dog-care questions.

## Main AI Feature: Retrieval-Augmented Generation (RAG)

PawPal+ uses a small local dog-care knowledge base and a transparent retrieval process. The app calls the OpenAI Responses API for answer generation, while local evidence and guardrail checks help keep the response grounded and safe.

1. The user selects a dog from the schedule and optionally edits that dog's profile.
2. Input guardrails check for emergencies, medication-dose requests, non-dog questions, and empty input.
3. The retriever selects the most relevant dog-care records from the local knowledge base.
4. The retrieved records, dog profile, and question are added to the LLM prompt.
5. The LLM generates a short answer grounded in the retrieved context.
6. PawPal+ displays the answer, sources, and a veterinary disclaimer.

## Architecture Overview

The system is split into a rule-based scheduler and an AI care guide. The scheduler is the original deterministic module that manages tasks and plans. The AI tab uses retrieval plus guardrails to build a prompt for the OpenAI API, then displays the generated answer with sources. The architecture diagram is available in [`diagrams/system_architecture.mmd`](diagrams/system_architecture.mmd).

## Project Structure

```text
.
├── app.py                         # Streamlit interface
├── main.py                        # Original scheduler CLI demo
├── pawpal_system.py               # Original OOP scheduler
├── ai_assistant.py                # Guardrails, retrieval, and LLM call
├── knowledge_base.json            # Curated dog-care records
├── requirements.txt               # Python dependencies
├── tests/                         # Automated tests
├── diagrams/
│   ├── system_architecture.mmd     # Final AI system diagram
│   └── uml_final.mmd               # Original OOP class diagram
├── docs/
│   └── evaluation_results.md      # Parseable human evaluation
├── model_card.md                  # Responsible-AI reflection
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the OpenAI API key

Export the environment variable required to call the OpenAI API. Do not commit API keys to GitHub.

```bash
export OPENAI_API_KEY="your-api-key"
```

### 5. Run the application

```bash
streamlit run app.py
```

### 6. Run automated tests

```bash
python -m pytest -q
```

## Sample Interactions

### Example 1: Feeding routine

```text
Input: How often should I feed my adult dog?
Output: Adult dogs are commonly fed on a consistent schedule, often with two meals per day. Exact needs depend on the dog’s size, activity level, and health. Follow the food label and your veterinarian’s advice.
```

**Why it matters:** This shows the AI using local care guidance to answer a routine feeding question.

### Example 2: Exercise guidance

```text
Input: How much exercise does an adult dog need?
Output: Most adult dogs benefit from at least 30 minutes to one hour of daily activity. The exact amount depends on breed, age, and health, and it should be adjusted for weather and fatigue.
```

**Why it matters:** This demonstrates retrieval of exercise guidance plus a human-friendly explanation.

### Example 3: Emergency guardrail

```text
Input: My dog cannot breathe. What should I do?
Output: This may be an emergency. Contact an emergency veterinarian immediately. PawPal+ cannot diagnose or replace professional veterinary care.
```

**Why it matters:** This proves the system can safely redirect urgent questions rather than generating unsafe medical advice.

## Sample End-to-End Execution

This output shows a full AI pipeline run with retrieval, guardrails, and sources.

```text
QUESTION: How often should I feed my adult dog?
STATUS: ok
ANSWER: Grounded answer [1].
SOURCES: [{'title': 'AAHA Nutrition and Weight Management Guidelines', 'url': 'https://www.aaha.org/resources/2021-aaha-nutrition-and-weight-management-guidelines/', 'document_id': 'feeding_schedule'}, {'title': 'ASPCA General Dog Care', 'url': 'https://www.aspca.org/pet-care/dog-care/general-dog-care', 'document_id': 'bathing_grooming'}]

QUESTION: My dog cannot breathe. What should I do?
STATUS: emergency
ANSWER: This may be an emergency. Contact an emergency veterinarian immediately. PawPal+ cannot diagnose or replace veterinary care.
SOURCES: []

QUESTION: How should I care for my cat?
STATUS: unsupported_species
ANSWER: PawPal+ currently supports dogs only. Please use a species-specific trusted resource or veterinarian for another animal.
SOURCES: []
```

**Why it matters:** This run shows the system using retrieval and grounding for a routine question, while also enforcing safety guardrails for emergencies and unsupported species.

## Design Decisions and Trade-offs

- **Local JSON knowledge base + keyword retrieval:** This approach is easy to inspect, version-control, and test. It avoids the complexity of embeddings or a vector database, which is appropriate for a portfolio MVP.
- **Read-only AI generation:** The assistant only suggests information and does not modify the scheduler. That keeps the original deterministic scheduling logic stable and reduces risk from incorrect model outputs.
- **Safety-first guardrails:** Guardrails for medication requests, emergencies, non-dog questions, and empty input improve safety, even though they make the assistant more cautious.
- **Dog-only scope:** Narrowing the system to dogs keeps the data and prompts focused. The trade-off is that the project does not support cats or other animal species.
- **Simple retrieval over advanced search:** Transparent keyword scoring is easier to explain and debug. It may miss some phrasing variations, but it makes the system more predictable and testable.
- **Environment robustness:** Real proxy and package issues during development encouraged clearer API setup and fallback behavior, reinforcing a stable core retrieval pipeline.

## Reliability and Testing Summary

The project uses multiple reliability mechanisms:

- Automated tests for retrieval, empty input, emergency detection, medication safety, unsupported questions, and source output.
- Logging for retrieval choices, guardrail events, successful responses, and OpenAI API failures.
- Structured human evaluation in [`docs/evaluation_results.md`](docs/evaluation_results.md).
- Reproducible command output in [`docs/demo_output.md`](docs/demo_output.md).

**Current verification:** `python3 -m pytest -q` was executed successfully with 24 tests passing. The Streamlit app and live OpenAI API integration were both verified successfully, and both tabs work correctly. Six human UI smoke tests were run and passed; all 10 structured evaluation cases are now documented.

## Reflection

This project taught me how applied AI is strongest when it is combined with deterministic software logic and clear safety boundaries. The scheduler remains the reliable core, while the AI layer provides context-aware explanation without taking over medical decisions.

The graded responsible-AI reflection is documented in `model_card.md`.

## Limitations

- The system supports dogs only.
- The local knowledge base covers a limited set of routine-care topics.
- Keyword retrieval may miss synonyms or indirect phrasing.
- The AI output can still be incomplete or misleading even when context is provided.
- PawPal+ is not a veterinarian and does not diagnose, prescribe, or determine medication dosage.
- Emergency warnings rely on a fixed phrase list and may not catch every urgent situation.

## Responsible Use

PawPal+ provides educational information only. Users should verify important decisions with a qualified veterinarian and seek immediate professional help for emergencies.
