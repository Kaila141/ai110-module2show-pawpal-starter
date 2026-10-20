from datetime import date, timedelta

from pawpal_system import Owner, PlanEntry, Pet, Priority, Scheduler, Task, format_time


def main() -> None:
    # Owner, available 7-9 AM and 5-8 PM (times are minutes since midnight)
    owner = Owner("Kaila")
    owner.set_availability([(7 * 60, 9 * 60), (17 * 60, 20 * 60)])

    # Two pets
    buddy = Pet("Buddy", "Dog")
    mia = Pet("Mia", "Cat")
    owner.add_pet(buddy)
    owner.add_pet(mia)

    # Tasks with different durations, priorities and frequencies
    # Added deliberately out of order (not by duration, priority or pet)
    mia.add_task(Task("Play", 20, "Laser pointer", Priority.MEDIUM))
    buddy.add_task(Task("Walk", 30, "Walk around the neighborhood", Priority.HIGH, frequency=2))
    mia.add_task(Task("Give medication", 5, "Thyroid pill", Priority.HIGH))
    buddy.add_task(Task("Train tricks", 25, "Practice sit and stay", Priority.MEDIUM))
    buddy.add_task(Task("Brush fur", 15, "Brush out loose fur", Priority.LOW))
    mia.add_task(Task("Feed", 10, "Wet food", Priority.HIGH, frequency=2))

    scheduler = Scheduler(owner, date.today())
    scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    scheduler.display_plan()

    print()
    print("Why this plan:")
    print(scheduler.explain_plan())

    # Mark a couple of tasks done so the completion filter has something to show
    for _, task in scheduler.filter_tasks(pet_name="Buddy"):
        if task.name in ("Brush fur", "Train tricks"):
            task.mark_complete()

    def show(title, pairs):
        print()
        print(title)
        if not pairs:
            print("  (none)")
        for pet, task in pairs:
            status = "done" if task.is_completed else "pending"
            print(f"  {pet.name:<6} {task.name:<16} {task.duration:>2} min  "
                  f"{task.priority.name:<6} {status}")

    print()
    print("=" * 40)
    print("Sorting and filtering checks")
    print("=" * 40)
    show("sort_tasks() - priority, then duration:", scheduler.sort_tasks())
    show("sort_by_time() - duration, then priority:", scheduler.sort_by_time())
    show("filter_tasks(completed=True):", scheduler.filter_tasks(completed=True))
    show("filter_tasks(completed=False):", scheduler.filter_tasks(completed=False))
    show("filter_tasks(pet_name='mia'):", scheduler.filter_tasks(pet_name="mia"))
    show("filter_tasks(completed=False, pet_name='Buddy'):",
         scheduler.filter_tasks(completed=False, pet_name="Buddy"))
    show("filter_tasks(pet_name='Rex') - no such pet:", scheduler.filter_tasks(pet_name="Rex"))

    # Recurring tasks: completing a daily/weekly task adds the next occurrence
    print()
    print("=" * 40)
    print("Recurring task check")
    print("=" * 40)
    daily = Task("Daily meds", 5, "Morning pill", Priority.HIGH, recurrence="daily")
    weekly = Task("Bath", 30, "Full bath", Priority.MEDIUM, recurrence="weekly")
    once = Task("Vet visit", 60, "Annual checkup", Priority.HIGH)
    for t in (daily, weekly, once):
        buddy.add_task(t)
    for t in (daily, weekly, once):
        new = scheduler.complete_task(buddy, t)
        if new:
            print(f"  {t.name}: done -> next '{new.name}' ({t.recurrence}) due {new.due_date}")
        else:
            print(f"  {t.name}: done -> no next occurrence (one-off)")

    tomorrow = Scheduler(owner, date.today() + timedelta(days=1))
    tomorrow.generate_plan()
    names = [e.task.name for e in tomorrow.entries]
    print(f"  Tomorrow's plan includes 'Daily meds': {'Daily meds' in names}")
    today = Scheduler(owner, date.today())
    today.generate_plan()
    print(f"  Today's plan includes 'Daily meds': {'Daily meds' in [e.task.name for e in today.entries]}")

    # Conflict detection: the scheduler never overlaps tasks itself, so place two by hand
    print()
    print("=" * 40)
    print("Conflict detection check")
    print("=" * 40)
    check = Scheduler(owner, date.today())
    check.generate_plan()
    print(f"  Generated plan conflicts: {check.detect_conflicts() or 'none'}")

    walk = Task("Vet call", 30, "Phone the vet", Priority.HIGH)
    groom = Task("Grooming", 45, "Groom coat", Priority.MEDIUM)
    # Same pet and different pets, all starting at 6:00 PM
    check.entries.append(PlanEntry(buddy, walk, 18 * 60, 18 * 60 + 30, "manual"))
    check.entries.append(PlanEntry(buddy, groom, 18 * 60, 18 * 60 + 45, "manual"))
    check.entries.append(PlanEntry(mia, walk, 18 * 60 + 15, 18 * 60 + 25, "manual"))
    for warning in check.detect_conflicts():
        print(f"  {warning}")

    available = ", ".join(f"{format_time(s)} - {format_time(e)}" for s, e in owner.available_time_slots)
    print()
    print(f"Owner availability: {available}")


if __name__ == "__main__":
    main()
