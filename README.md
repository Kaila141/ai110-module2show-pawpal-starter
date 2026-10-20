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

## ✨ Features

- Priority sorting: Tasks are ranked high to low priority, with shorter tasks first when priorities tie. The daily plan is built in this order.
- Duration sorting: Tasks can also be listed shortest first (ties go to the higher priority).
- Time-ordered schedule: The finished plan is always shown from the earliest task to the latest, regardless of the order the tasks were added.
- Spread-out repeats: A task done several times a day (like two walks) is spaced across your available hours instead of stacked together.
- Multiple pets: One owner can have many pets, and the plan fits all of their tasks into one shared day.
- Filtering: Narrow the task list by pet name and/or whether tasks are done or still to do.
- Daily and weekly recurrence: Completing a repeating task automatically adds the next one, due the next day or the next week. Tasks that aren't due yet are left out of today's plan.
- Conflict warnings: If two scheduled tasks ever overlap, a warning names both and their times instead of crashing. The scheduler also refuses to book overlapping times in the first place.
- Unscheduled tasks: Anything that doesn't fit the available time is listed with a suggestion, rather than silently dropped.
- Plan explanations: Each scheduled task comes with a short reason for why it landed at that time.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage (requires pytest-cov):
pytest --cov=pawpal_system --cov-report=term-missing
```

Sample test output:

```
============= test session starts ==============
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Amand\Coding\CodePath AI110\ai110-module2show-pawpal-starter
configfile: ov
plugins: anyio-4.15.1
collected 26 items                              

test\test_pawpal.py ..................... [ 80%]
.....                                     [100%]

============== 26 passed in 0.06s ==============
```

### What the tests cover

The tests cover the scheduling logic in pawpal_system.py:

- Sorting: It tests different sorting orders (priority first then time first), ties, ordering across multiple pets, empty owners, and ensuring the plan prints in chronological order.
- Recurrence: It tests that new occurences are created for reoccuring tasks that are completed while one-off tasks create nothing. It also tests that dates roll over month and year ends. Future-dated copies are not scheduled early.
- Plan generation: multi-occurrence tasks are spread across the day, completed tasks are skipped, tasks that don't fit land in `unscheduled_tasks`, plans never overlap, and regenerating gives the same plan.
- Conflict detection: duplicate start times are flagged, overlapping and out-of-window bookings are rejected, and back-to-back tasks are not treated as conflicts.
- Filtering: by completion status and pet name (case-insensitive), combined, and with an unknown pet.

I would give this a 4/5 confidence level. All 26 tests pass and  cover the core behaviors and their edge cases, but I held back a star because of ucnertainty where sort_by_time orders by duration, not clock time. Also since multiple-day scheduling isn't tested either.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_tasks(), Scheduler.sort_by_time() | sort_tasks() orders by highest priority, then shortest duration, and is what generate_plan() uses. sort_by_time() orders by shortest duration, then highest priority. |
| Filtering | Scheduler.filter_tasks(completed, pet_name) | Returns (pet, task) pairs matching a completion status (True/False) and/or a pet name (case-insensitive). Leave a filter as None to skip it. |
| Conflict handling | Scheduler.detect_conflicts() | Compares every plan entry's start and end times, for the same pet or different pets, and returns a warning message for each overlapping pair instead of raising an error. An empty list means no conflicts. |
| Recurring tasks | Task.next_occurrence(), Scheduler.complete_task() | A task's recurrence can be "daily" or "weekly". Completing it with complete_task() adds a new copy to the pet, due today + 1 day (daily) or today + 7 days (weekly). generate_plan() skips tasks whose due_date is in the future. |

## 📸 Demo Walkthrough

### What you can do in the app

Run it with `streamlit run app.py`. The page works top to bottom:

- **Owner:** Enter your name and the hours you're free each day (default 7:00 AM to 8:00 PM).
- **Pets:** Add a pet by name and species. A small table shows each pet and how many tasks it has.
- **Tasks:** Add a task for a pet with a title, length in minutes, priority, how many times per day, and whether it repeats daily or weekly. Sort and filter the list, and mark tasks done.
- **Build Schedule:** Press one button to get today's plan, with a reason for every time slot.

### Example workflow

1. Add two pets: **Mochi** (a dog) and **Whiskers** (a cat).
2. Add tasks for Mochi:
   - **Morning walk**: 20 minutes, high priority, 2 times a day, repeats daily.
   - **Brush fur**: 15 minutes, low priority.
   - **Training**: 25 minutes, medium priority.
3. Add tasks for Whiskers:
   - **Give medication**: 5 minutes, high priority, repeats daily.
   - **Feed**: 10 minutes, high priority, 2 times a day.
   - **Play time**: 20 minutes, medium priority.
4. Use the **Pet**, **Status** and **Sort by** dropdowns to view your six tasks in different ways, such as only Whiskers's tasks, or shortest first.
5. Press **Generate schedule** to see today's plan. Both pets share one day, and the two-a-day tasks are split between morning and evening.
6. Mark **Give medication** complete. The app confirms the next dose is due tomorrow.
7. Press **Generate schedule** again. Today's plan no longer includes the finished medication, and the filters now show it as done.

### What the scheduler shows you

- Sorting: The most important, fastest tasks are placed first.
- Spacing: Tasks that repeat in a day are spread out, such as one walk in the morning and one in the evening.
- Conflict warnings: If two tasks ever overlap, a warning appears above the schedule naming both. A green message appears only when the plan is clean.
- Skipped tasks: If something can't fit in your free time, you're told which task and how to fix it.
- Explanations: Open "Why is the plan in this order?" to see the reasoning for each slot.

### Sample command-line output

`python main.py` runs the same scheduler without the web page. It builds a plan for two pets (Buddy the dog and Mia the cat), then runs checks on sorting, filtering, recurring tasks and conflict warnings. In the last check the app places tasks at overlapping times by hand, to show that the warnings appear.

```
========================================
Today's Schedule
========================================
Plan for Tuesday, October 20, 2026
  7:00 AM - 7:05 AM  Mia: Give medication
  7:05 AM - 7:15 AM  Mia: Feed
  7:15 AM - 7:45 AM  Buddy: Walk
  7:45 AM - 8:05 AM  Mia: Play
  8:05 AM - 8:30 AM  Buddy: Train tricks
  8:30 AM - 8:45 AM  Buddy: Brush fur
  5:00 PM - 5:10 PM  Mia: Feed
  5:10 PM - 5:40 PM  Buddy: Walk
Total scheduled: 145 min

Why this plan:
7:00 AM - 7:05 AM Mia: Give medication (High priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
7:05 AM - 7:15 AM Mia: Feed (High priority, occurrence 1 of 2; spaced through the day (aimed for 7:00 AM).)
7:15 AM - 7:45 AM Buddy: Walk (High priority, occurrence 1 of 2; spaced through the day (aimed for 7:00 AM).)
7:45 AM - 8:05 AM Mia: Play (Medium priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
8:05 AM - 8:30 AM Buddy: Train tricks (Medium priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
8:30 AM - 8:45 AM Buddy: Brush fur (Low priority, occurrence 1 of 1; spaced through the day (aimed for 7:00 AM).)
5:00 PM - 5:10 PM Mia: Feed (High priority, occurrence 2 of 2; spaced through the day (aimed for 1:30 PM).)
5:10 PM - 5:40 PM Buddy: Walk (High priority, occurrence 2 of 2; spaced through the day (aimed for 1:30 PM).)

========================================
Sorting and filtering checks
========================================

sort_tasks() - priority, then duration:
  Mia    Give medication   5 min  HIGH   pending
  Mia    Feed             10 min  HIGH   pending
  Buddy  Walk             30 min  HIGH   pending
  Mia    Play             20 min  MEDIUM pending
  Buddy  Train tricks     25 min  MEDIUM done
  Buddy  Brush fur        15 min  LOW    done

sort_by_time() - duration, then priority:
  Mia    Give medication   5 min  HIGH   pending
  Mia    Feed             10 min  HIGH   pending
  Buddy  Brush fur        15 min  LOW    done
  Mia    Play             20 min  MEDIUM pending
  Buddy  Train tricks     25 min  MEDIUM done
  Buddy  Walk             30 min  HIGH   pending

filter_tasks(completed=True):
  Buddy  Train tricks     25 min  MEDIUM done
  Buddy  Brush fur        15 min  LOW    done

filter_tasks(completed=False):
  Buddy  Walk             30 min  HIGH   pending
  Mia    Play             20 min  MEDIUM pending
  Mia    Give medication   5 min  HIGH   pending
  Mia    Feed             10 min  HIGH   pending

filter_tasks(pet_name='mia'):
  Mia    Play             20 min  MEDIUM pending
  Mia    Give medication   5 min  HIGH   pending
  Mia    Feed             10 min  HIGH   pending

filter_tasks(completed=False, pet_name='Buddy'):
  Buddy  Walk             30 min  HIGH   pending

filter_tasks(pet_name='Rex') - no such pet:
  (none)

========================================
Recurring task check
========================================
  Daily meds: done -> next 'Daily meds' (daily) due 2026-10-21
  Bath: done -> next 'Bath' (weekly) due 2026-10-27
  Vet visit: done -> no next occurrence (one-off)
  Tomorrow's plan includes 'Daily meds': True
  Today's plan includes 'Daily meds': False

========================================
Conflict detection check
========================================
  Generated plan conflicts: none
  Warning: Buddy: Vet call (6:00 PM - 6:30 PM) overlaps Buddy: Grooming (6:00 PM - 6:45 PM)
  Warning: Buddy: Vet call (6:00 PM - 6:30 PM) overlaps Mia: Vet call (6:15 PM - 6:25 PM)
  Warning: Buddy: Grooming (6:00 PM - 6:45 PM) overlaps Mia: Vet call (6:15 PM - 6:25 PM)

Owner availability: 7:00 AM - 9:00 AM, 5:00 PM - 8:00 PM
```
