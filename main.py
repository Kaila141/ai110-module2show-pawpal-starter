from datetime import date

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, format_time


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
    buddy.add_task(Task("Walk", 30, "Walk around the neighborhood", Priority.HIGH, frequency=2))
    buddy.add_task(Task("Brush fur", 15, "Brush out loose fur", Priority.LOW))
    mia.add_task(Task("Feed", 10, "Wet food", Priority.HIGH, frequency=2))
    mia.add_task(Task("Give medication", 5, "Thyroid pill", Priority.HIGH))
    mia.add_task(Task("Play", 20, "Laser pointer", Priority.MEDIUM))

    scheduler = Scheduler(owner, date.today())
    scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    scheduler.display_plan()

    print()
    print("Why this plan:")
    print(scheduler.explain_plan())

    available = ", ".join(f"{format_time(s)} - {format_time(e)}" for s, e in owner.available_time_slots)
    print()
    print(f"Owner availability: {available}")


if __name__ == "__main__":
    main()
