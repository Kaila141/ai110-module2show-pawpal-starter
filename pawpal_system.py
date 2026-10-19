from dataclasses import dataclass, field
from datetime import date as Date, time
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: Priority = Priority.MEDIUM
    is_completed: bool = False
    frequency: Optional[str] = None

    def mark_complete(self) -> None:
        pass

    def edit(self, **fields) -> None:
        pass


@dataclass
class Pet:
    name: str
    breed_species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    available_time_slots: List[Tuple[time, time]] = field(default_factory=list)  # (start, end)
    preferences: Dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        pass

    def set_availability(self, slots: List[Tuple[time, time]]) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        ...


class Scheduler:
    def __init__(self, owner: Owner, date: Date):
        self.owner = owner
        self.date = date
        self.entries: Dict[Task, Tuple[time, time, str]] = {}  # task -> (start, end, reason)
        self.reasoning: str = ""

    def generate_plan(self) -> None:
        pass

    def sort_tasks(self) -> List[Task]:
        ...

    def add_plan_entry(self, task: Task, start: time, end: time, reason: str) -> None:
        pass

    def get_total_duration(self) -> int:
        ...

    def display_plan(self) -> None:
        pass

    def explain_plan(self) -> str:
        ...

    def has_overlap(self, start: time, end: time) -> bool:
        ...
