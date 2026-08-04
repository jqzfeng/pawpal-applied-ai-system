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
3. The question, dog profile, and retrieved context are sent to the OpenAI API.
4. The prompt instructs the LLM to use only the supplied context for factual care claims.
5. The answer is returned with sources and a disclaimer.

## Safety and Reliability Measures

- Emergency terms trigger an immediate veterinary warning before the LLM is called.
- Medication-dose requests are declined and redirected to a veterinarian.
- Empty questions are handled without calling the model.
- Non-dog questions are rejected with a clear scope message.
- Sources are displayed so users can see what information grounded the answer.
- Logs record guardrail decisions, retrieved document identifiers, and errors without storing API keys.
- Automated tests and structured human evaluation check expected behavior.

## AI Collaboration Reflection

### How I Collaborated With AI

I used AI as a planning, coding, debugging, and documentation assistant. I started by defining a narrow dog-only scope, then used AI to help translate that plan into code and tests while verifying whether each suggestion matched the project requirements and existing PawPal+ architecture.

The AI was especially useful for drafting guardrails, structuring the prompt flow, and writing documentation that was clear across different agents.

### One Helpful AI Suggestion

A helpful suggestion was to use a small local knowledge base with transparent keyword retrieval instead of adding a vector database. This made the system reproducible, reduced setup time, and made retrieval behavior easy to inspect and test within the limited project timeline.

### One Flawed or Inappropriate AI Suggestion

An early AI direction recommended expanding PawPal+ to support multiple animal species, use a vector database, and automate more care-planning actions. That was too much scope for an MVP and increased testing risk. I rejected that path and kept the system limited to dogs, with a simple local knowledge base and read-only AI responses.

### Test Reliability Insight

The most surprising reliability finding was how effective the guardrails were in practice. Emergency and medication inputs were caught cleanly before the model generated a response, and surfacing sources made the AI output feel more trustworthy. The more difficult task was getting the model to admit when the local knowledge base was insufficient.

## Limitations or Biases

- The system’s accuracy is limited by the size and content of the local dog-care knowledge base.
- Keyword retrieval is sensitive to phrasing and may miss synonyms or less direct questions.
- PawPal+ is dog-only and does not support cats or other animals.
- It is not veterinary advice and should not be used as a medical diagnosis or prescription tool.
- Emergency detection relies on a fixed phrase list and cannot catch every possible urgent description.

## Misuse and Prevention

The AI could be misused if someone treated it as professional veterinary advice. To prevent that, the system explicitly redirects medication and emergency questions to a veterinarian, displays sourcing for factual claims, and keeps the AI response layer read-only.

## How I Verified AI Contributions

I compared AI-generated suggestions against the assignment rubric, kept the scheduler and AI modules separate, reviewed generated code, and ran automated tests. I also used manual smoke tests and structured evaluation in `docs/evaluation_results.md` to check retrieval relevance, source display, emergency handling, and missing-context behavior.

## Evaluation Status

- Automated test functions passed: **24**
- Structured human evaluation completed: **6 passed / 6 run**
- Total planned evaluation cases: **10**
- Remaining structured evaluation cases: **4 TBD**
- Main observed failure mode: **None observed in the six completed smoke tests**
- Change made after evaluation: **Updated documentation to reflect verified pytest, Streamlit, and human UI results.**

## Ethical and Responsible-AI Considerations

The system presents uncertainty and sources rather than claiming professional authority. It minimizes medical risk by blocking medication-dose advice, escalating emergencies, limiting support to routine dog-care topics, and requiring the human user to decide what action to take.
