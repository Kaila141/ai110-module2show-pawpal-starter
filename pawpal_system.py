from dataclasses import dataclass, field
from datetime import date as Date
from enum import Enum
from typing import Dict, List, Optional, Tuple

# All times are stored as minutes since midnight (e.g. 8:00 AM = 480, 1:30 PM = 810).
Minutes = int


def format_time(minutes: Minutes) -> str:
    """Convert minutes since midnight to a readable string like '8:00 AM'."""
    hours, mins = divmod(minutes, 60)
    suffix = "AM" if hours % 24 < 12 else "PM"
    return f"{hours % 12 or 12}:{mins:02d} {suffix}"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    duration: int  # minutes per occurrence
    description: str = ""
    priority: Priority = Priority.MEDIUM
    is_completed: bool = False
    frequency: int = 1  # times per day, entered by the owner (e.g. 2 = twice a day)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def edit(self, **fields) -> None:
        """Update the given fields (at a minimum, name and duration) on this task."""
        for key, value in fields.items():
            if not hasattr(self, key):
                raise ValueError(f"Task has no field '{key}'")
            setattr(self, key, value)


@dataclass
class Pet:
    name: str
    breed_species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time_slots: List[Tuple[Minutes, Minutes]] = field(default_factory=list)  # (start, end)
    preferences: Dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def set_availability(self, slots: List[Tuple[Minutes, Minutes]]) -> None:
        """Replace the owner's available time slots with the given (start, end) slots."""
        self.available_time_slots = list(slots)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return every task across all pets, paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class PlanEntry:
    pet: Pet
    task: Task
    start: Minutes
    end: Minutes
    reason: str


class Scheduler:
    def __init__(self, owner: Owner, date: Date):
        """Create an empty plan for the given owner and date."""
        self.owner = owner
        self.date = date
        self.entries: List[PlanEntry] = []
        self.unscheduled_tasks: List[Tuple[Pet, Task]] = []
        self.reasoning: str = ""

    def generate_plan(self) -> None:
        """Rebuild the plan from scratch, spreading each task's occurrences through the day."""
        # Occurrence i aims for day_start + i * (window / frequency) and takes the first open
        # time at or after it, falling back to the earliest open time anywhere. Occurrences
        # that still don't fit go to unscheduled_tasks (one per miss); the rest are scheduled.
        self.entries = []
        self.unscheduled_tasks = []
        self.reasoning = ""

        slots = self.owner.available_time_slots
        day_start = min((s for s, _ in slots), default=0)
        day_end = max((e for _, e in slots), default=0)

        for pet, task in self.sort_tasks():
            if task.is_completed:
                continue
            gap = (day_end - day_start) / task.frequency
            for occurrence in range(task.frequency):
                target = day_start + round(occurrence * gap)
                start = self.find_slot(task.duration, earliest=target)
                placement = f"spaced through the day (aimed for {format_time(target)})"
                if start is None:
                    start = self.find_slot(task.duration)
                    placement = f"no room after {format_time(target)}, so used the earliest open time"
                if start is None:
                    self.unscheduled_tasks.append((pet, task))
                    continue
                reason = (
                    f"{task.priority.name.title()} priority, occurrence "
                    f"{occurrence + 1} of {task.frequency}; {placement}."
                )
                self.add_plan_entry(pet, task, start, start + task.duration, reason)

        self.reasoning = self.explain_plan()

    def sort_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return the owner's (pet, task) pairs sorted by highest priority, then shortest duration."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda pair: (-pair[1].priority.value, pair[1].duration),
        )

    def find_slot(self, duration: int, earliest: Minutes = 0) -> Optional[Minutes]:
        """Return the earliest open start time at or after `earliest` that fits `duration`, or None."""
        for slot_start, slot_end in sorted(self.owner.available_time_slots):
            start = max(slot_start, earliest)
            while start + duration <= slot_end:
                # End times of entries that collide with [start, start + duration)
                blocking = [e.end for e in self.entries
                            if start < e.end and start + duration > e.start]
                if not blocking:
                    return start
                start = max(blocking)  # jump past the conflicting entries
        return None

    def add_plan_entry(self, pet: Pet, task: Task, start: Minutes, end: Minutes, reason: str) -> bool:
        """Add an entry if it fits an available slot without overlapping; return whether it was added."""
        if start >= end:
            return False
        inside_slot = any(s <= start and end <= e for s, e in self.owner.available_time_slots)
        if not inside_slot or self.has_overlap(start, end):
            return False
        self.entries.append(PlanEntry(pet, task, start, end, reason))
        return True

    def get_total_duration(self) -> int:
        """Total minutes of all tasks in entries."""
        return sum(e.end - e.start for e in self.entries)

    def display_plan(self) -> None:
        """Print the plan in time order, showing each entry's pet, task and times."""
        print(f"Plan for {self.date.strftime('%A, %B %d, %Y')}")
        if not self.entries:
            print("  (nothing scheduled)")
        for e in sorted(self.entries, key=lambda e: e.start):
            print(f"  {format_time(e.start)} - {format_time(e.end)}  {e.pet.name}: {e.task.name}")
        print(f"Total scheduled: {self.get_total_duration()} min")
        for pet, task in self.unscheduled_tasks:
            print(f"  Not scheduled: {pet.name}: {task.name}")

    def explain_plan(self) -> str:
        """Return the reasoning for each entry and for any unscheduled tasks."""
        lines = []
        for e in sorted(self.entries, key=lambda e: e.start):
            lines.append(
                f"{format_time(e.start)} - {format_time(e.end)} {e.pet.name}: {e.task.name} "
                f"({e.reason})"
            )
        missed = {}  # id(task) -> [pet, task, number of occurrences that didn't fit]
        for pet, task in self.unscheduled_tasks:
            missed.setdefault(id(task), [pet, task, 0])[2] += 1
        for pet, task, count in missed.values():
            lines.append(
                f"Not scheduled: {pet.name}: {task.name} - {count} of {task.frequency} "
                f"occurrence(s) had no open {task.duration}-minute slot."
            )
        return "\n".join(lines) if lines else "No tasks scheduled."

    def has_overlap(self, start: Minutes, end: Minutes) -> bool:
        """Return True if [start, end) overlaps any existing entry."""
        return any(start < e.end and end > e.start for e in self.entries)
