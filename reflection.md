# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Core Actions:
A user should be able to perform the following core actions with this app:
* Owner can add tasks for multiple pets and generate a plan including all of them
* Generates a plan in priority order 
* Multi-occurence tasks are spread out in a day
* Sorting tasks by time returns in the right order
* Completing a recurring task creates a new occurence to be scheduled later

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

My scheduler considers time constraints, like the owner's availability and priority of tasks. I felt that to was more important for availability to matter more, but if I were to redo this assignent, I would make it so that priority matters more so that things like vet appointments can stretch into unavailable time slots and the owner can approve of it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that it greedily adds tasks to the plan in order of priority (then shortest duration) and puts each one in the first open slot, and it never moves a task once it's placed. This means the plan isn't guaranteed to fit the most tasks possible, since a different arrangement could sometimes leave room for a task that ends up unscheduled. I think this is reasonable because a pet owner only has a handful of tasks and a few hours of availability, so a complex search isn't worth it. It also makes sure the most important tasks (like medication and feeding) get placed first.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude to help with brainstorming, implementation, and refactoring. With every output, I would go through it thoroughly to ensure I understand what it was doing. If there was something I didn't understand, then I would prompt it to further explain what it did or suggested. For instance, some of the design changes that I made above were done only after I asked Claude to explain the change.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One instance was with how Claude suggested representing the frequency. My first thought was to make it a string so users entered how often they wished the task to be done. When I asked for feedback and bottlenecks of my design, Claude pointed out an issue with case comparisons and the risk of the user entering a value that doesn't make sense. So it suggested making it an Enum of values: "once, daily, weekly, monthly". I didn't quite like that idea because it didn't account for cases where tasks should be done multiple times a day, among others. When I raised this point, it then suggsted making frequency a Frequency(times, per) class with a Period enum (day, week, month) so that tasks could repeat per day, week, or month. I actualy liked this idea, but when it said that I would have to track the completion history for weekly and monthly tasks to know if they've been done already, I decided against it. Then, I decided to revisit the problem statement to see if there were any requirements or suggestions placed for frequency. That's when I saw that it mentioned daily routines. So, I told Claude that supporting longer periods would eb out of scope for now and that frequency was best kept as a simple times per-day number that the owner enters. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The tests cover the scheduling logic in pawpal_system.py:
- Sorting: It tests different sorting orders (priority first then time first), ties, ordering across multiple pets, empty owners, and ensuring the plan prints in chronological order.
- Recurrence: It tests that new occurences are created for reoccuring tasks that are completed while one-off tasks create nothing. It also tests that dates roll over month and year ends. Future-dated copies are not scheduled early.
- Plan generation: multi-occurrence tasks are spread across the day, completed tasks are skipped, tasks that don't fit land in `unscheduled_tasks`, plans never overlap, and regenerating gives the same plan.
- Conflict detection: duplicate start times are flagged, overlapping and out-of-window bookings are rejected, and back-to-back tasks are not treated as conflicts.
- Filtering: by completion status and pet name (case-insensitive), combined, and with an unknown pet.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I would give this a 4/5 confidence level. All 26 tests pass and  cover the core behaviors and their edge cases, but I held back a star because of ucnertainty where sort_by_time orders by duration, not clock time. Also since multiple-day scheduling isn't tested either.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am satisfied with the process. I learned a lot about being a lead architect while using AI tools. There was a lot of back and forth as I decided what features would be best to include and which ones were out of scope.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration of this process, I would improve the deisgn to consider other constraints like owner preferences and allowing high priority tasks to optionally override the available time slots.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

It is important to ensure I understand the problem statement and if not, ask AI to help explain it to me too. That was a mistake I made at the beginning, where most of my time was spent trying to understand the system myself instead of brainstorming with AI.

Also, using multiple sessions helped keep context from getting muddled. So it could focus on giving edge cases without the context of the implementation influencing that.