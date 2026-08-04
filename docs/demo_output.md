# PawPal+ Reproducible Execution Output

This file captures reproducible command output from the repository.

## Automated Tests

```bash
python3 -m pytest -q
```

```text
24 passed in 0.03s
```

## Sample End-to-End System Run

```bash
python3 - <<'PY'
from ai_assistant import answer_question

profile = {"name": "Mochi", "life stage": "Adult"}
questions = [
    "How often should I feed my adult dog?",
    "My dog cannot breathe. What should I do?",
    "How should I care for my cat?"
]
for q in questions:
    result = answer_question(q, profile, generator=lambda prompt: "Grounded answer [1].")
    print('QUESTION:', q)
    print('STATUS:', result['status'])
    print('ANSWER:', result['answer'])
    print('SOURCES:', result['sources'])
    print()
PY
```

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
