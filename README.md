# PawPal+ AI Dog Care Guide

## Title and Summary

PawPal+ combines the original rule-based care scheduler with a dog-only AI care assistant. The assistant answers basic questions about feeding, food safety, exercise, bathing, grooming, dental care, and enrichment. It retrieves relevant information from a curated local knowledge base and gives that context to a large language model (LLM), helping the system produce grounded answers with visible sources.

This project matters because dog owners often need quick, understandable routine-care guidance. PawPal+ makes general information easier to access while using guardrails to redirect emergency and medication questions to a veterinarian.

## Original Project

The original project was **PawPal+ (Module 2 Project)**, an object-oriented pet-care scheduling application. It represented owners, pets, tasks, time windows, and daily plans through Python classes and used deterministic scheduling logic to prioritize tasks, detect simple conflicts, and create recurring care tasks.

This final project extends that scheduler with an AI-powered, retrieval-augmented dog-care guide. The original scheduling classes remain the reliable rule-based layer, while the new AI feature supports everyday dog-care questions.

## Main AI Feature: Retrieval-Augmented Generation (RAG)

PawPal+ uses a small local dog-care knowledge base and a transparent retrieval process:

1. The user selects a dog from the schedule and optionally edits that dog's profile.
2. Input guardrails check for emergencies, medication-dose requests, and empty input.
3. The retriever selects the most relevant dog-care records from the local knowledge base.
4. The retrieved records, dog profile, and question are added to the LLM prompt.
5. The LLM generates a short answer grounded in the retrieved context.
6. PawPal+ displays the answer, sources, and a veterinary disclaimer.

The retrieved information meaningfully changes the prompt and the resulting answer; it is not merely printed beside a generic response.

## Supported Topics

- Feeding routines
- General food safety
- Exercise and walking
- Bathing and grooming
- Dental care
- Nail care
- Hydration
- Mental enrichment
- General preventive-care reminders

PawPal+ supports dogs only. It does not diagnose illness, prescribe treatment, or determine medication dosage.

## Architecture Overview

The system diagram is stored as Mermaid source at [`diagrams/system_architecture.mmd`](diagrams/system_architecture.mmd). The application separates the reliable rule-based scheduler from the AI care guide. Within the AI flow, guardrails screen the input first, the retriever selects local evidence, and the LLM produces a grounded response. Automated tests and structured human evaluation check the system, while the user reviews every answer before acting on it.

The original OOP class diagram is stored at [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd).

## Project Structure

```text
.
├── app.py                         # Streamlit interface
├── main.py                        # Original scheduler CLI demo
├── pawpal_system.py               # Original OOP scheduler
├── ai_assistant.py                # Guardrails, retrieval, and LLM call
├── knowledge_base.json            # Curated dog-care records
├── requirements.txt               # Python dependencies
├── tests/                          # Automated tests
├── diagrams/
│   ├── system_architecture.mmd     # Final AI system diagram
│   └── uml_final.mmd               # Original OOP class diagram
├── docs/
│   └── evaluation_results.md       # Parseable human evaluation
├── model_card.md                   # Responsible-AI reflection
└── README.md
```

The RAG backend, Streamlit interface, knowledge base, tests, diagrams, and documentation in this structure are implemented in the current project package.

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

### 4. Configure the LLM API key

Export the environment variable required by the selected LLM provider. Do not commit API keys to GitHub.

```bash
export OPENAI_API_KEY="your-api-key"
```

### 4.1 Make the AI search work

When network access is available, install the OpenAI Python package:

```bash
pip install openai
```

Then set your API key in the shell:

```bash
export OPENAI_API_KEY="your-api-key"
```

If the OpenAI SDK is not installed or network access is restricted, the app can still attempt a direct HTTP request to the OpenAI Responses API as a fallback.

### 5. Run the application

```bash
streamlit run app.py
```

### 6. Run automated tests

```bash
python -m pytest
```

## Sample Interactions

The following are target interactions for the final implementation. Replace them with copied outputs from the running application before submission if the wording changes.

### Example 1: Feeding routine

**Input:** `How often should I feed my adult dog?`

**Expected output:** Adult dogs are commonly fed on a consistent schedule, often divided into two meals per day. Exact needs depend on the dog's size, activity, health, and the calorie content of the food. Follow the food label and your veterinarian's advice.

**Expected source:** Curated dog-feeding guidance in the local knowledge base.

### Example 2: Exercise

**Input:** `How much exercise does my senior dog need?`

**Expected output:** Senior dogs can benefit from regular, lower-impact activity such as shorter walks. The amount should be adjusted to mobility, health, weather, and signs of fatigue.

**Expected source:** Curated dog-exercise guidance in the local knowledge base.

### Example 3: Emergency guardrail

**Input:** `My dog cannot breathe. What should I do?`

**Expected output:** This may be an emergency. Contact an emergency veterinarian immediately. PawPal+ cannot diagnose or replace veterinary care.

## Design Decisions and Trade-offs

- **Dog-only scope:** Supporting one species keeps the knowledge base focused and makes the three-hour MVP easier to test.
- **Local curated knowledge base:** Local records are reproducible and easy to inspect. The trade-off is limited topic coverage.
- **Simple transparent retrieval:** Keyword-based scoring is faster to build and easier to test than a vector database. It may miss synonyms or differently worded questions.
- **LLM for explanation, rules for safety:** The LLM creates readable responses, while deterministic code handles emergency and medication guardrails.
- **Human confirmation:** AI suggestions are informational and are never automatically added to the schedule or treated as medical decisions.

## Reliability and Testing Summary

The final project uses three reliability mechanisms:

1. Automated tests for retrieval, empty input, emergency detection, medication safety, unsupported questions, and source output.
2. Logging for retrieval choices, guardrail events, successful responses, and API failures.
3. Structured human evaluation in [`docs/evaluation_results.md`](docs/evaluation_results.md).

**Current verification:** All 24 scheduler and AI test functions passed by direct execution, and Python syntax compilation passed. This workspace does not include `pytest`, so a standard `python -m pytest -q` run remains pending after dependency installation. Human evaluation and real LLM sample-output review also remain pending.

## Reflection

This project showed me the difference between deterministic software logic and an applied AI system. The original PawPal+ scheduler follows rules I wrote, while the new RAG feature retrieves evidence and uses an LLM to create a context-sensitive response. I also learned that a useful AI feature needs boundaries, visible sources, failure handling, and evaluation—not only a model call.

The graded responsible-AI reflection, including AI collaboration, one helpful suggestion, one flawed suggestion, and system limitations, is documented in [`model_card.md`](model_card.md).

## Limitations

- The system supports dogs only.
- The local knowledge base covers a limited set of routine-care topics.
- Keyword retrieval may fail when the user's wording differs from stored keywords.
- LLM output can still be incomplete or misleading even when context is provided.
- PawPal+ is not a veterinarian and does not diagnose, prescribe, or determine medication dosage.
- Emergency warnings depend on a limited set of phrases and cannot identify every urgent situation.

## Responsible Use

PawPal+ provides general educational information. Users should verify important decisions with a qualified veterinarian and seek immediate professional help for emergencies.
