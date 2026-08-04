# PawPal+ AI Dog Care Guide — AI Agent Handoff

## Purpose of This Document

This file is the shared implementation brief for Claude or any AI coding agent that continues the project in VS Code. Read it before changing code. Preserve the intentionally small scope unless the human owner explicitly expands it.

## Assignment Requirements Interpreted

The final project must extend the earlier Module 1–3 project with a useful AI feature integrated into the main application. It must run reproducibly, include logging or guardrails, show a Mermaid source diagram, provide setup instructions and sample interactions, and include a parseable reliability evaluation.

Repository setup requirements shown in the course instructions:

- Work in a new public GitHub repository copied from the original repository.
- Preserve the original code and commit history.
- Do not initialize the new remote with a README, license, or `.gitignore` before pushing the copied project.
- Include an `assets/` folder for architecture images.
- Include a `diagrams/` folder and submit the architecture diagram as Mermaid source (`.mmd` or Mermaid in `.md`). A PNG alone is insufficient.

## Agreed Product Scope

Project name: **PawPal+ AI Dog Care Guide**

Original project: PawPal+, an OOP-based Python pet-care scheduler with `Owner`, `Pet`, `Task`, `TimeWindow`, `ScheduledTask`, `DailyPlan`, and `Scheduler` classes.

New applied-AI feature: a dog-only Retrieval-Augmented Generation (RAG) care assistant.

Supported routine topics include:

- Feeding routines
- Common food safety
- Exercise and walking
- Bathing and grooming
- Dental care
- Mental enrichment
- General preventive care

Explicitly out of scope:

- Cats or other animal species
- Diagnosis or treatment
- Medication selection or dosage
- Exact food portions
- Vector database or embeddings
- Multi-agent workflows
- AI automatically changing the scheduler
- Login, persistence, or a UI redesign

## Brainstormed Design and Decisions

The main AI feature is RAG. Reliability is demonstrated through deterministic guardrails, logging, automated tests, visible sources, and a structured human evaluation.

The RAG sequence is:

1. Receive a question and optional dog profile.
2. Handle empty, non-dog, emergency, and medication inputs with deterministic rules.
3. Search a curated local JSON knowledge base using transparent keyword overlap.
4. Put retrieved records, the dog profile, and the question into the LLM prompt.
5. Require the LLM to ground factual claims in that context.
6. Return the answer with sources.

Why keyword retrieval: it is reproducible, inspectable, easy to test, and appropriate for a three-hour MVP. Its known trade-off is weaker handling of synonyms than embedding retrieval.

Why the LLM is read-only: generated advice can be wrong. It must not automatically add, remove, or change scheduled care tasks. The human reviews the answer.

## Current Implementation Status

Implemented:

- `ai_assistant.py`
  - JSON loading and validation
  - Keyword-overlap retrieval
  - Emergency, medication, empty-input, and unsupported-species guardrails
  - Grounded prompt construction
  - OpenAI Responses API call
  - Source collection
  - Logging and safe API error handling
- `knowledge_base.json`
  - Eight dog-care records with IDs, keywords, content, source titles, and URLs
- `app.py`
  - Streamlit dog profile form
  - Question input and RAG call
  - Status-specific UI messages
  - Visible sources and disclaimer
- `tests/test_ai_assistant.py`
  - Ten tests covering retrieval, guardrails, missing context, profile use, sources, and model errors
- Documentation
  - `README.md`
  - `model_card.md`
  - `docs/evaluation_results.md`
  - `diagrams/system_architecture.mmd`
  - `diagrams/uml_final.mmd`
  - `assets/README.md`
  - `.gitignore`
- `requirements.txt` includes Streamlit, pytest, and OpenAI.

Integration and verification already performed in the Codex workspace:

- The original scheduler UI and the AI guide are merged into two tabs in `app.py`.
- The original `main.py`, scheduler tests, and full `diagrams/uml_final.mmd` remain in place.
- The duplicate root-level `uml_final.mmd` from the ZIP was intentionally not added.
- The chocolate record now cites the directly relevant Merck Veterinary Manual page.
- Python syntax compilation passed for the application, backend, scheduler, CLI demo, and tests.
- All 24 test functions (14 scheduler and 10 AI) passed by direct execution.
- The first smoke check exposed a substring bug where `cat` matched the word `medication`; guardrail matching was changed to phrase/word-boundary matching.
- Full pytest was not available in the Codex runtime because pytest was not installed there. Run it in the project virtual environment before claiming a pass count.

## Required Next Steps in VS Code

Do these in order:

1. Create and activate a virtual environment.
2. Run `pip install -r requirements.txt`.
3. Run `python -m pytest -q` and fix any failures.
4. Add `OPENAI_API_KEY` to the environment. Optionally set `OPENAI_MODEL`; the current default is `gpt-4o-mini`.
5. Run `streamlit run app.py` and verify both tabs.
6. Manually test at least these inputs:
   - `How often should I feed my adult dog?`
   - `How much exercise does my senior dog need?`
   - `How often should I bathe my dog?`
   - `Can my dog eat chocolate?`
   - `My dog cannot breathe. What should I do?`
   - `Should I double my dog's medication dose?`
7. Copy actual outputs into README sample interactions.
8. Fill every `TBD` in `docs/evaluation_results.md`, `model_card.md`, and README using real results only.
9. If an architecture PNG is generated, save it in `assets/` and optionally embed it in README. Keep `diagrams/system_architecture.mmd` because it is the graded source.
10. Review `git diff`, commit, push, and verify files and commit history on GitHub.

## Important Implementation Notes

- Tests inject a fake generator, so they should not call the real OpenAI API or require an API key.
- `answer_question()` is the main pipeline entry point.
- The retrieved context must remain inside the model prompt. Merely displaying sources beside an ungrounded answer would not satisfy the RAG requirement.
- Do not log API keys, full environment variables, or unnecessary personal information.
- Do not claim clinical validation or professional veterinary authority.
- Keep source display enabled.
- If the installed OpenAI SDK or selected model rejects the call, update only `call_openai()` and preserve the rest of the pipeline interface.
- Keep the scheduler and AI guide as separate tabs so later changes do not remove either working feature.

## Definition of Done

The MVP is complete when:

- The app launches from the documented setup steps.
- A normal dog-care question retrieves relevant local evidence and produces an LLM answer with sources.
- Emergency and medication prompts bypass ordinary generation.
- Unsupported or missing-context questions fail safely.
- Automated test results are recorded honestly.
- At least three real sample interactions appear in README.
- `model_card.md` contains the required responsible-AI reflection and actual evaluation totals.
- The Mermaid architecture source is committed.
- GitHub contains the code, documentation, and original history.
