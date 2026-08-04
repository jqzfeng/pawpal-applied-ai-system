# PawPal+ AI Dog Care Guide — Model Card

## System Purpose

PawPal+ AI Dog Care Guide answers general, low-risk dog-care questions using retrieval-augmented generation (RAG). It is designed for routine topics such as feeding, exercise, bathing, grooming, dental care, and enrichment.

## Intended Users and Uses

The intended user is a dog owner seeking basic educational guidance. Appropriate uses include asking about routine feeding schedules, general exercise considerations, grooming frequency, and common food-safety reminders.

## Out-of-Scope Uses

PawPal+ must not be used to:

- Diagnose a medical condition
- Replace a veterinarian
- Choose, change, or calculate medication dosage
- Delay emergency veterinary care
- Provide authoritative guidance for cats or other animals

## How the AI System Works

1. Deterministic guardrails inspect the question.
2. A local retriever selects relevant dog-care records.
3. The question, dog profile, and retrieved context are sent to an LLM.
4. The prompt instructs the LLM to use only the supplied context for factual care claims.
5. The answer is returned with its sources and a disclaimer.

## Safety and Reliability Measures

- Emergency terms trigger an immediate veterinary warning before the LLM is called.
- Medication-dose requests are declined and redirected to a veterinarian.
- Empty questions are handled without calling the model.
- If retrieval confidence is too low, the system states that its local information is insufficient.
- Sources are displayed so users can see what information grounded the answer.
- Logs record guardrail decisions, retrieved document identifiers, and errors without storing API keys.
- Automated tests and structured human evaluation check expected behavior.

## AI Collaboration Reflection

### How I Collaborated With AI

I used AI as a planning, coding, debugging, and documentation assistant. I first defined a small dog-only scope, selected RAG as the required advanced AI feature, and specified the expected file structure and safety behavior. I then used AI to help translate that plan into code and tests, while reviewing whether each suggestion matched the project requirements and existing PawPal+ architecture.

### One Helpful AI Suggestion

A helpful suggestion was to use a small local knowledge base with transparent keyword retrieval instead of adding a vector database. This made the system reproducible, reduced setup time, and made retrieval behavior easy to inspect and test within the limited project timeline.

### One Flawed or Inappropriate AI Suggestion

An earlier direction suggested broader features such as multiple animal species, a vector database, and more automated planning behavior. Those additions were not appropriate for a three-hour MVP because they would increase implementation and testing risk without being required by the rubric. I narrowed the product to dogs and kept the AI action read-only.

### How I Verified AI Contributions

I compared suggestions against the assignment rubric, kept the original scheduler responsibilities separate from the AI module, reviewed generated code, and ran automated tests. I also used structured sample questions to manually check retrieval relevance, source display, emergency handling, and insufficient-context behavior.

## Known Limitations

- The system's accuracy is limited by the size and quality of its local knowledge base.
- Keyword matching is sensitive to wording and may retrieve weak context for synonyms.
- The LLM may still generate unsupported or overconfident language.
- Rule-based emergency detection cannot recognize every possible emergency description.
- General advice may not fit a dog's breed, age, health, allergies, or medical history.
- The system has not been clinically validated.

## Evaluation Status

Automated and human-evaluation results should be copied here after the final implementation is run.

- Automated test functions passed in direct workspace execution: **24**
- Automated test functions total: **24**
- Full `pytest` run after dependency installation: **TBD**
- Human evaluation passed: **TBD**
- Human evaluation total: **TBD**
- Main observed failure mode: **TBD**

## Ethical and Responsible-AI Considerations

The system presents uncertainty and sources rather than claiming professional authority. It minimizes medical risk by blocking medication-dose advice, escalating emergencies, limiting support to routine dog-care topics, and requiring the human user to decide what action to take.
