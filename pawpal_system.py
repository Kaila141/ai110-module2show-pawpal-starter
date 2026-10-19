from dataclasses import dataclass, field
from datetime import date as Date
from enum import Enum
from typing import Dict, List, Optional, Tuple

# All times are stored as minutes since midnight (e.g. 8:00 AM = 480, 1:30 PM = 810).
Minutes = int


def format_time(minutes: Minutes) -> str:
    """Convert minutes since midnight to a readable string like '8:00 AM'."""
    ...


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    duration: int  # minutes per occurrence
    priority: Priority = Priority.MEDIUM
    is_completed: bool = False
    frequency: int = 1  # times per day, entered by the owner (e.g. 2 = twice a day)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def edit(self, **fields) -> None:
        """Update the given fields (at a minimum, name and duration) on this task."""
        pass


@dataclass
class Pet:
    name: str
    breed_species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time_slots: List[Tuple[Minutes, Minutes]] = field(default_factory=list)  # (start, end)
    preferences: Dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def set_availability(self, slots: List[Tuple[Minutes, Minutes]]) -> None:
        """Replace the owner's available time slots with the given (start, end) slots."""
        pass

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return every task across all pets, paired with the pet it belongs to."""
        ...


@dataclass
class PlanEntry:
    pet: Pet
    task: Task
    start: Minutes
    end: Minutes
    reason: str


class Scheduler:
    def __init__(self, owner: Owner, date: Date):
        self.owner = owner
        self.date = date
        self.entries: List[PlanEntry] = []
        self.unscheduled_tasks: List[Tuple[Pet, Task]] = []
        self.reasoning: str = ""

    def generate_plan(self) -> None:
        """Clear entries, unscheduled_tasks and reasoning, then rebuild the plan.

        For each sorted task (once per occurrence in task.frequency), find a slot with
        find_slot and add it with add_plan_entry; tasks with no slot go to unscheduled_tasks.
        """
        pass

    def sort_tasks(self) -> List[Tuple[Pet, Task]]:
        """Sort the owner's tasks; Priority is an Enum, so sort with key=task.priority.value."""
        ...

    def find_slot(self, duration: int) -> Optional[Minutes]:
        """Return the earliest start time where `duration` minutes fit in an available slot
        without overlapping an existing entry, or None if there is no room."""
        ...

    def add_plan_entry(self, pet: Pet, task: Task, start: Minutes, end: Minutes, reason: str) -> bool:
        """Add an entry if it doesn't overlap another entry and sits inside an available slot.

        Returns True if added, False if rejected.
        """
        ...

    def get_total_duration(self) -> int:
        """Total minutes of all tasks in entries."""
        ...

    def display_plan(self) -> None:
        """Print the plan in time order, showing each entry's pet, task and times."""
        pass

    def explain_plan(self) -> str:
        """Return the reasoning for each entry and for any unscheduled tasks."""
        ...

    def has_overlap(self, start: Minutes, end: Minutes) -> bool:
        """Return True if [start, end) overlaps any existing entry."""
        ...
