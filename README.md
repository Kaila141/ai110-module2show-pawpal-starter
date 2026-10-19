# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
========================================
Today's Schedule
========================================
Plan for Monday, October 19, 2026
  7:00 AM - 7:05 AM  Mia: Give medication
  7:05 AM - 7:15 AM  Mia: Feed
  7:15 AM - 7:45 AM  Buddy: Walk
  7:45 AM - 8:05 AM  Mia: Play
  8:05 AM - 8:20 AM  Buddy: Brush fur
  5:00 PM - 5:10 PM  Mia: Feed
  5:10 PM - 5:40 PM  Buddy: Walk
Total scheduled: 120 min

Why this plan:
7:00 AM - 7:05 AM Mia: Give medication (High priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
7:05 AM - 7:15 AM Mia: Feed (High priority, occurrence 1 of 2; spaced through the day (aimed for 7:00 AM).)
7:15 AM - 7:45 AM Buddy: Walk (High priority, occurrence 1 of 2; spaced through the day (aimed for 7:00 AM).)
7:45 AM - 8:05 AM Mia: Play (Medium priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
8:05 AM - 8:20 AM Buddy: Brush fur (Low priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
5:00 PM - 5:10 PM Mia: Feed (High priority, occurrence 2 of 2; spaced through the day (aimed for 1:30 PM).)
5:10 PM - 5:40 PM Buddy: Walk (High priority, occurrence 2 of 2; spaced through the day (aimed for 1:30 PM).)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
