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

## Implementation Summary
PawPal+ is a daily pet-care scheduler built around four core classes in pawpal_system.py (Owner, Pet, Task, Scheduler) and an extra, class for PlanEntry. An Owner has several Pets and a set of available time windows, and each Pet keeps its own list of Tasks. A Task is one care activity, such as a walk, a feeding or a medication. It has a description, a duration in minutes, a priority, a completion flag, and a frequency that says how many times a day it should happen. Each placement is stored as a PlanEntry that records the pet, task, start and end times, and the reason it was put there.

The Owner exposes a single method, get_all_tasks(), that gathers every pet's tasks together and pairs each one with its pet. The Scheduler reads from that method rather than from any one pet, which is what makes the plan work across multiple pets. To build a plan, the Scheduler sorts those tasks by priority, then by duration. It then places each task's occurrences at times spread throughout the owner's available window, so a twice daily task occurs in the morning and evening. For every occurrence it finds the first available time that doesn't overlap anything already scheduled. If a recurring task can't fit, it's skipped, and the ones that do remain scheduled. Anything that doesn't are recorded as unscheduled. The Scheduler can then print the day's plan, total up the scheduled minutes, and explain why each task is where it is and why any were skipped.

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

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_tasks(), Scheduler.sort_by_time() | sort_tasks() orders by highest priority, then shortest duration, and is what generate_plan() uses. sort_by_time() orders by shortest duration, then highest priority. |
| Filtering | Scheduler.filter_tasks(completed, pet_name) | Returns (pet, task) pairs matching a completion status (True/False) and/or a pet name (case-insensitive). Leave a filter as None to skip it. |
| Conflict handling | Scheduler.detect_conflicts() | Compares every plan entry's start and end times, for the same pet or different pets, and returns a warning message for each overlapping pair instead of raising an error. An empty list means no conflicts. |
| Recurring tasks | Task.next_occurrence(), Scheduler.complete_task() | A task's recurrence can be "daily" or "weekly". Completing it with complete_task() adds a new copy to the pet, due today + 1 day (daily) or today + 7 days (weekly). generate_plan() skips tasks whose due_date is in the future. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
