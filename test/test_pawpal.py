import sys
from pathlib import Path

# Make pawpal_system importable when pytest is run from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


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
