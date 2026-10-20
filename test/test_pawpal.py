import sys
from datetime import date
from pathlib import Path

# Make pawpal_system importable when pytest is run from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, PlanEntry, Priority, Scheduler, Task

TODAY = date(2026, 10, 20)


def make_scheduler(*pets, slots=((480, 1200),)):
    """Owner available 8:00 AM - 8:00 PM by default, with the given pets."""
    owner = Owner("Sam", list(pets))
    owner.set_availability(list(slots))
    return Scheduler(owner, TODAY)


def names(pairs):
    return [task.name for _, task in pairs]


def snapshot(scheduler):
    return [(e.pet.name, e.task.name, e.start, e.end) for e in scheduler.entries]


def test_mark_complete_changes_task_status():
    task = Task("Walk", 30)
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Walk", 30))

    assert len(pet.tasks) == 1


# --- Required tests: sorting, recurrence, conflict detection ---------------

def test_plan_is_displayed_in_chronological_order(capsys):
    """Entries stored out of order (evening, morning, midday) print earliest-to-latest."""
    buddy = Pet("Buddy", "Dog")
    scheduler = make_scheduler(buddy)
    scheduler.add_plan_entry(buddy, Task("Evening", 30), 1080, 1110, "")
    scheduler.add_plan_entry(buddy, Task("Morning", 30), 480, 510, "")
    scheduler.add_plan_entry(buddy, Task("Midday", 30), 720, 750, "")

    scheduler.display_plan()

    out = capsys.readouterr().out
    assert out.index("Morning") < out.index("Midday") < out.index("Evening")


def test_completing_daily_task_creates_task_for_following_day():
    pet = Pet("Buddy", "Dog")
    walk = Task("Walk", 30, recurrence="daily", due_date=TODAY)
    pet.add_task(walk)
    scheduler = make_scheduler(pet)

    new_task = scheduler.complete_task(pet, walk)

    assert walk.is_completed is True
    assert new_task is not None and new_task is not walk
    assert new_task.due_date == date(2026, 10, 21)
    assert new_task.is_completed is False
    assert new_task in pet.tasks and len(pet.tasks) == 2


def test_detect_conflicts_flags_duplicate_start_times():
    buddy, whiskers = Pet("Buddy", "Dog"), Pet("Whiskers", "Cat")
    scheduler = make_scheduler(buddy, whiskers)
    # Bypass add_plan_entry (which rejects overlaps) to simulate a bad plan.
    scheduler.entries = [
        PlanEntry(buddy, Task("Walk", 30), 540, 570, ""),
        PlanEntry(whiskers, Task("Feed", 15), 540, 555, ""),
    ]

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Buddy: Walk" in warnings[0] and "Whiskers: Feed" in warnings[0]
    assert "9:00 AM" in warnings[0]


def test_scheduler_refuses_to_book_two_tasks_at_same_time():
    buddy = Pet("Buddy", "Dog")
    scheduler = make_scheduler(buddy)

    assert scheduler.add_plan_entry(buddy, Task("Walk", 30), 540, 570, "") is True
    assert scheduler.add_plan_entry(buddy, Task("Feed", 15), 540, 555, "") is False
    assert scheduler.detect_conflicts() == []


# --- Sorting ---------------------------------------------------------------

def test_sort_tasks_orders_by_priority_then_duration():
    pet = Pet("Buddy", "Dog")
    pet.add_task(Task("low-short", 5, priority=Priority.LOW))
    pet.add_task(Task("high-long", 60, priority=Priority.HIGH))
    pet.add_task(Task("med", 20, priority=Priority.MEDIUM))
    pet.add_task(Task("high-short", 10, priority=Priority.HIGH))

    result = make_scheduler(pet).sort_tasks()

    assert names(result) == ["high-short", "high-long", "med", "low-short"]


def test_sort_tasks_with_ties_is_stable():
    pet = Pet("Buddy", "Dog")
    for name in ("first", "second", "third"):
        pet.add_task(Task(name, 15, priority=Priority.MEDIUM))

    assert names(make_scheduler(pet).sort_tasks()) == ["first", "second", "third"]


def test_sort_tasks_spans_multiple_pets():
    buddy, whiskers = Pet("Buddy", "Dog"), Pet("Whiskers", "Cat")
    buddy.add_task(Task("buddy-low", 10, priority=Priority.LOW))
    buddy.add_task(Task("buddy-high", 10, priority=Priority.HIGH))
    whiskers.add_task(Task("whiskers-med", 10, priority=Priority.MEDIUM))
    whiskers.add_task(Task("whiskers-high", 20, priority=Priority.HIGH))

    result = make_scheduler(buddy, whiskers).sort_tasks()

    assert names(result) == ["buddy-high", "whiskers-high", "whiskers-med", "buddy-low"]
    assert [pet.name for pet, _ in result][:2] == ["Buddy", "Whiskers"]


def test_sort_with_no_pets_or_no_tasks_returns_empty_list():
    assert make_scheduler().sort_tasks() == []
    assert make_scheduler(Pet("Buddy", "Dog")).sort_tasks() == []
    assert make_scheduler().sort_by_time() == []


def test_sort_by_time_orders_by_duration_then_priority():
    pet = Pet("Buddy", "Dog")
    pet.add_task(Task("long", 60, priority=Priority.HIGH))
    pet.add_task(Task("short-low", 10, priority=Priority.LOW))
    pet.add_task(Task("short-high", 10, priority=Priority.HIGH))

    result = make_scheduler(pet).sort_by_time()

    assert names(result) == ["short-high", "short-low", "long"]


# --- Recurrence ------------------------------------------------------------

def test_complete_weekly_task_creates_occurrence_seven_days_out():
    pet = Pet("Buddy", "Dog")
    bath = Task("Bath", 30, recurrence="weekly", due_date=TODAY)
    pet.add_task(bath)

    new_task = make_scheduler(pet).complete_task(pet, bath)

    assert new_task is not None
    assert new_task.due_date == date(2026, 10, 27)


def test_complete_one_off_task_creates_no_new_task():
    pet = Pet("Buddy", "Dog")
    vet = Task("Vet visit", 60)
    pet.add_task(vet)

    result = make_scheduler(pet).complete_task(pet, vet)

    assert result is None
    assert vet.is_completed is True
    assert len(pet.tasks) == 1


def test_next_occurrence_is_independent_copy_of_original():
    original = Task(
        "Meds", 5, description="with food", priority=Priority.HIGH,
        frequency=2, recurrence="daily", due_date=TODAY,
    )
    original.mark_complete()

    copy = original.next_occurrence(TODAY)

    assert copy is not None
    assert copy is not original
    assert copy.is_completed is False and original.is_completed is True
    assert (copy.name, copy.duration, copy.description, copy.priority, copy.frequency, copy.recurrence) == (
        "Meds", 5, "with food", Priority.HIGH, 2, "daily",
    )
    copy.edit(name="Changed")
    assert original.name == "Meds"


def test_next_occurrence_across_month_and_year_boundary():
    daily = Task("Walk", 30, recurrence="daily")
    weekly = Task("Bath", 30, recurrence="weekly")

    year_end = daily.next_occurrence(date(2026, 12, 31))
    month_end = daily.next_occurrence(date(2026, 1, 31))
    weekly_wrap = weekly.next_occurrence(date(2026, 12, 28))

    assert year_end is not None and year_end.due_date == date(2027, 1, 1)
    assert month_end is not None and month_end.due_date == date(2026, 2, 1)
    assert weekly_wrap is not None and weekly_wrap.due_date == date(2027, 1, 4)


def test_completing_same_recurring_task_twice_adds_two_copies():
    """Documents current behavior: complete_task has no double-completion guard."""
    pet = Pet("Buddy", "Dog")
    walk = Task("Walk", 30, recurrence="daily", due_date=TODAY)
    pet.add_task(walk)
    scheduler = make_scheduler(pet)

    scheduler.complete_task(pet, walk)
    scheduler.complete_task(pet, walk)

    assert len(pet.tasks) == 3


def test_future_due_task_is_not_scheduled_today():
    pet = Pet("Buddy", "Dog")
    pet.add_task(Task("Today", 30, due_date=TODAY))
    pet.add_task(Task("Tomorrow", 30, due_date=date(2026, 10, 21)))
    scheduler = make_scheduler(pet)

    scheduler.generate_plan()

    assert [e.task.name for e in scheduler.entries] == ["Today"]
    assert scheduler.unscheduled_tasks == []


# --- Plan generation / spreading ------------------------------------------

def test_generate_plan_spreads_multi_occurrence_task_across_day():
    pet = Pet("Buddy", "Dog")
    pet.add_task(Task("Feed", 15, frequency=3))
    scheduler = make_scheduler(pet)  # 8:00 AM - 8:00 PM

    scheduler.generate_plan()

    starts = sorted(e.start for e in scheduler.entries)
    assert starts == [480, 720, 960]  # 8:00 AM, 12:00 PM, 4:00 PM


def test_generate_plan_skips_completed_tasks():
    pet = Pet("Buddy", "Dog")
    done = Task("Done", 30)
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Pending", 30))
    scheduler = make_scheduler(pet)

    scheduler.generate_plan()

    assert [e.task.name for e in scheduler.entries] == ["Pending"]


def test_generate_plan_puts_unfittable_tasks_in_unscheduled():
    pet = Pet("Buddy", "Dog")
    too_long = Task("Marathon", 800)  # window is only 720 minutes
    pet.add_task(too_long)
    pet.add_task(Task("Walk", 30))
    scheduler = make_scheduler(pet)

    scheduler.generate_plan()

    assert [e.task.name for e in scheduler.entries] == ["Walk"]
    assert scheduler.unscheduled_tasks == [(pet, too_long)]

    no_availability = make_scheduler(pet, slots=())
    no_availability.generate_plan()
    assert no_availability.entries == []
    assert len(no_availability.unscheduled_tasks) == 2


def test_generate_plan_has_no_overlapping_entries():
    buddy, whiskers = Pet("Buddy", "Dog"), Pet("Whiskers", "Cat")
    for i in range(4):
        buddy.add_task(Task(f"b{i}", 45, frequency=2, priority=Priority.HIGH))
        whiskers.add_task(Task(f"w{i}", 30, frequency=3))
    scheduler = make_scheduler(buddy, whiskers)

    scheduler.generate_plan()

    assert scheduler.detect_conflicts() == []
    ordered = sorted(scheduler.entries, key=lambda e: e.start)
    assert all(a.end <= b.start for a, b in zip(ordered, ordered[1:]))


def test_generate_plan_is_idempotent():
    pet = Pet("Buddy", "Dog")
    pet.add_task(Task("Walk", 30, frequency=2))
    pet.add_task(Task("Marathon", 800))
    scheduler = make_scheduler(pet)

    scheduler.generate_plan()
    first, first_missed = snapshot(scheduler), list(scheduler.unscheduled_tasks)
    scheduler.generate_plan()

    assert snapshot(scheduler) == first
    assert scheduler.unscheduled_tasks == first_missed


# --- Filtering & conflicts -------------------------------------------------

def test_filter_tasks_by_completed_and_pet_name_case_insensitive():
    buddy, whiskers = Pet("Buddy", "Dog"), Pet("Whiskers", "Cat")
    walk, feed, play = Task("Walk", 30), Task("Feed", 10), Task("Play", 15)
    walk.mark_complete()
    buddy.add_task(walk)
    buddy.add_task(feed)
    whiskers.add_task(play)
    scheduler = make_scheduler(buddy, whiskers)

    assert names(scheduler.filter_tasks()) == ["Walk", "Feed", "Play"]
    assert names(scheduler.filter_tasks(pet_name="buddy")) == ["Walk", "Feed"]
    assert names(scheduler.filter_tasks(completed=True)) == ["Walk"]
    assert names(scheduler.filter_tasks(completed=False)) == ["Feed", "Play"]
    assert names(scheduler.filter_tasks(completed=False, pet_name="BUDDY")) == ["Feed"]


def test_filter_tasks_unknown_pet_returns_empty_list():
    buddy = Pet("Buddy", "Dog")
    buddy.add_task(Task("Walk", 30))

    assert make_scheduler(buddy).filter_tasks(pet_name="Rex") == []


def test_add_plan_entry_rejects_overlap_and_out_of_slot_times():
    buddy = Pet("Buddy", "Dog")
    scheduler = make_scheduler(buddy)  # 480-1200
    task = Task("Walk", 30)

    assert scheduler.add_plan_entry(buddy, task, 600, 630, "") is True
    assert scheduler.add_plan_entry(buddy, task, 615, 645, "") is False  # overlaps
    assert scheduler.add_plan_entry(buddy, task, 450, 480, "") is False  # before the day
    assert scheduler.add_plan_entry(buddy, task, 1190, 1220, "") is False  # runs past the slot
    assert scheduler.add_plan_entry(buddy, task, 700, 700, "") is False  # empty
    assert scheduler.add_plan_entry(buddy, task, 720, 700, "") is False  # backwards
    assert len(scheduler.entries) == 1


def test_back_to_back_entries_are_not_conflicts():
    buddy = Pet("Buddy", "Dog")
    scheduler = make_scheduler(buddy)

    assert scheduler.add_plan_entry(buddy, Task("Walk", 30), 510, 540, "") is True
    assert scheduler.add_plan_entry(buddy, Task("Feed", 15), 540, 555, "") is True
    assert scheduler.detect_conflicts() == []
