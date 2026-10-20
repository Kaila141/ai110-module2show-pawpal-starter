import streamlit as st

from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("Plan your pets' care for the day: add pets and tasks, then generate a schedule.")

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Create the Owner once; later reruns reuse the one stored in the session "vault".
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
owner = st.session_state.owner
owner.name = owner_name

st.markdown("**Available time window**")
col_a, col_b = st.columns(2)
with col_a:
    window_start = st.time_input("From", value=time(7, 0))
with col_b:
    window_end = st.time_input("Until", value=time(20, 0))
if window_start < window_end:
    owner.set_availability([(window_start.hour * 60 + window_start.minute,
                             window_end.hour * 60 + window_end.minute)])
else:
    st.error("The end of the window must be after the start.")

st.divider()

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_clicked = st.form_submit_button("Add pet")

if add_pet_clicked:
    if pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species))  # Owner.add_pet stores it on the owner
    else:
        st.error("Please enter a pet name.")

if owner.pets:
    st.table([{"Pet": p.name, "Species": p.breed_species, "Tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=False):
        target_pet = owner.pets[st.selectbox("Pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name)]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col4:
            frequency = st.number_input("Times per day", min_value=1, max_value=10, value=1)
        repeats = st.selectbox("Repeats", ["Does not repeat", "daily", "weekly"])
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        # Pet.add_task stores the new Task on the chosen pet
        target_pet.add_task(
            Task(task_title, int(duration), priority=Priority[priority.upper()], frequency=int(frequency),
                 recurrence=None if repeats == "Does not repeat" else repeats)
        )

# A Scheduler for today drives the task list below (sorting, filtering, completing).
view = Scheduler(owner, date.today())
all_tasks = owner.get_all_tasks()  # every pet's tasks, paired with their pet

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

if all_tasks:
    st.markdown("**Current tasks**")
    f1, f2, f3 = st.columns(3)
    with f1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
    with f2:
        status_filter = st.selectbox("Status", ["All", "To do", "Done"])
    with f3:
        sort_choice = st.selectbox("Sort by", ["Priority (high first)", "Duration (shortest first)"])

    ordered = view.sort_tasks() if sort_choice.startswith("Priority") else view.sort_by_time()
    matching = view.filter_tasks(
        completed={"All": None, "To do": False, "Done": True}[status_filter],
        pet_name=None if pet_filter == "All pets" else pet_filter,
    )
    matching_ids = {id(t) for _, t in matching}
    visible = [(pet, t) for pet, t in ordered if id(t) in matching_ids]

    if visible:
        st.table([
            {"Pet": pet.name, "Task": t.name, "Minutes": t.duration,
             "Priority": t.priority.name.title(), "Times/day": t.frequency,
             "Repeats": (t.recurrence or "-").title(),
             "Due": t.due_date.strftime("%a %b %d") if t.due_date else "-",
             "Status": "✅ Done" if t.is_completed else "To do"}
            for pet, t in visible
        ])
        st.caption(f"Showing {len(visible)} of {len(all_tasks)} tasks.")
    else:
        st.info("No tasks match those filters.")

    to_do = view.filter_tasks(completed=False)
    if to_do:
        with st.form("complete_task_form", clear_on_submit=True):
            pet_task = to_do[st.selectbox(
                "Mark a task done", range(len(to_do)),
                format_func=lambda i: f"{to_do[i][0].name}: {to_do[i][1].name}",
            )]
            complete_clicked = st.form_submit_button("Mark complete")
        if complete_clicked:
            pet, task = pet_task
            next_task = view.complete_task(pet, task)  # recurring tasks queue their next occurrence
            if next_task and next_task.due_date:
                st.session_state.flash = (
                    f"Marked {pet.name}: {task.name} done. Next one is due "
                    f"{next_task.due_date.strftime('%A, %B %d')}."
                )
            else:
                st.session_state.flash = f"Marked {pet.name}: {task.name} done."
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not all_tasks:
        st.warning("Add at least one task first.")
    elif not owner.available_time_slots:
        st.warning("Set a valid available time window first.")
    else:
        scheduler = Scheduler(owner, date.today())
        scheduler.generate_plan()

        st.markdown(f"**Today's Schedule** ({scheduler.date.strftime('%A, %B %d')})")

        # Conflicts come first so they can't be missed. Each one names both tasks and what to do.
        conflicts = scheduler.detect_conflicts()
        for message in conflicts:
            st.warning(
                f"⚠️ Double-booked: {message.removeprefix('Warning: ')}\n\n"
                "**To fix:** shorten one of these tasks, or widen your available window and regenerate."
            )

        if scheduler.entries:
            if not conflicts:
                st.success(
                    f"All set! {len(scheduler.entries)} task(s) scheduled, "
                    f"{scheduler.get_total_duration()} minutes total, with no conflicts."
                )
            st.table([
                {"Time": f"{format_time(e.start)} - {format_time(e.end)}",
                 "Pet": e.pet.name, "Task": e.task.name, "Why": e.reason}
                for e in sorted(scheduler.entries, key=lambda e: e.start)
            ])

        for pet, task in scheduler.unscheduled_tasks:
            st.warning(
                f"Couldn't fit {pet.name}: {task.name} ({task.duration} min). "
                "Try widening your available window or shortening the task."
            )

        with st.expander("Why is the plan in this order?"):
            for e in sorted(scheduler.entries, key=lambda e: e.start):
                st.markdown(f"- **{e.pet.name}: {e.task.name}** — {e.reason}")
