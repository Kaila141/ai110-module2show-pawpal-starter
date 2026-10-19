# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Core Actions:
A user should be able to perform the following core actions with this app:
* Add a pet
* Feed the pet
* See today's care tasks for the pet 

Main Objects:
* Owner
    Attributes: name, Pets, available time slots, preferences
    Methods: add pet, set availability, get all tasks
* Pet
    Attributes: name, breed/species, tasks
    Methods: add pet task, remove task
* Task
    Attributes: name, duration, priority (enum: low, medium, high), isCompleted, unscheduled tasks, frequency?
    Methods: mark complete, edit
* Scheduler
    Attributes: owner, date, entries (dict: task, start time, end time, reason), reasoning
    Methods: gnerate plan, sort tasks, add plan entry, get total duration, display plan, explain plan, has overlap/does task fit

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
I chose four main classes for PawPal+:
* **Owner**: This class represents the person using the app. It stores basic information about the owner (name, pets, available time slots, and preferences). Availabiltiy and preferences were included as constraints of the owner that influence the plan. The responsibility of this class is to add pets to an owner, set their availabilities, and retrieve all the taks they have to do for their pets.
* **Pet**: The pet class represents a single animal. It holds the pet's name, breed, and respective care tasks. Its responsibilities are to add and remove tasks. Tasks are tied to the pet rather than the owner because different pets may have different tasks to be done to them (Eg: you'd walk your dog but not your fish).
* **Task**: This represents a single care activity, like take on a walk, feed, give mediciation, groom, etc. It stores a name, duration, priority, whether it is completed or not, and a frequency. The priority is an enum of values low, medium, and high. Frequency was added to account for recurring tasks (eg: daily, weekly, etc). There are methods for marking it completed and editing it.
* **Scheduler**: This class is for putting together a plan and providing a reasoning for the items in it. It references the owner (so it can access their pets, tasks, and availability), the day it's for, a list of scheduled task entries (each entry has a task, a start time, and an end time), and the reasoning behind the choices of tasks. I is responsible for sorting tasks (by priority or duration), generating a daily plan, checking whether a task fits in a time slot or overlaps with another, calculating the total scheduled time, displaying the plan, and giving a reason for why each task is where it is on the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed after I had Claude review the code skeleton. The top 5 changes include:
* An entry is represented as a class (PlanEntry) instead of a dictionary. This would represent one line of the daily plan. It stores the pet, task, start and end times, and the reason the task was placed there. Its there to describe a scheduled item. I made this change because Claude pointed out that a dict keyed by a Task dataclass wouldn't work since dataclasses aren't hashable by default and that the same task could appear multiple times (frequency). It also keeps the Scheduler focused on building the plan instead of storing entry details, so Scheduler holds a list of PlanEntry objects.
* get_all_tasks now returns (pet, task) instead of just task. This way it's clear which pet is associated with what task. 
* Times are stored as minutes since midnight. Sinc edurations are already in minutes, this makes end time computations and checking for overlaps simpler without having to consider dat/time arithmetic. A helper class (format_time) was added to handle display.
* Unscheduled tasks were part of my original design that I dropped because I wasn't sure about it. But then Claude suggested that it makes sense to include them so that the reasoning could also explain why certain tasks weren't included.
* Frequency is a number the owner enters. This represents the number of times a day the task should be completed. I considered a (count, period) pair so weekly or monthly tasks could be supported but realized this may be out of scope since the app is for daily routines, and weekly/monthly tasks would need to track completion history.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
