import streamlit as st

from datetime import date, time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

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
        target_pet = st.selectbox("Pet", owner.pets, format_func=lambda p: p.name)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col4:
            frequency = st.number_input("Times per day", min_value=1, max_value=10, value=1)
        add_task_clicked = st.form_submit_button("Add task")

    if add_task_clicked:
        # Pet.add_task stores the new Task on the chosen pet
        target_pet.add_task(
            Task(task_title, int(duration), priority=Priority[priority.upper()], frequency=int(frequency))
        )

all_tasks = owner.get_all_tasks()  # every pet's tasks, paired with their pet
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {"Pet": pet.name, "Task": t.name, "Minutes": t.duration,
         "Priority": t.priority.name.title(), "Times/day": t.frequency}
        for pet, t in all_tasks
    ])
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
        if scheduler.entries:
            st.table([
                {"Time": f"{format_time(e.start)} - {format_time(e.end)}",
                 "Pet": e.pet.name, "Task": e.task.name, "Why": e.reason}
                for e in sorted(scheduler.entries, key=lambda e: e.start)
            ])
        st.caption(f"Total scheduled: {scheduler.get_total_duration()} minutes")

        for pet, task in scheduler.unscheduled_tasks:
            st.warning(f"Couldn't fit {pet.name}: {task.name} ({task.duration} min)")
