"""Streamlit entry point for the PawPal+ scheduler and AI Dog Care Guide."""

from datetime import datetime

import streamlit as st

from ai_assistant import answer_question
from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan dog-care tasks and ask grounded questions about everyday dog care.")


def initialize_schedule_state() -> None:
    """Create the default owner and dog once per Streamlit session."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Jordan")
    if "pet" not in st.session_state:
        st.session_state.pet = Pet(name="Mochi", species="dog")
    if not any(
        pet.name == st.session_state.pet.name and pet.species == st.session_state.pet.species
        for pet in st.session_state.owner.pets
    ):
        st.session_state.owner.add_pet(st.session_state.pet)


def render_schedule_tab() -> None:
    """Render the original deterministic PawPal+ scheduler."""
    initialize_schedule_state()
    st.subheader("Owner and dog")
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
    pet_name = st.text_input("Dog name", value=st.session_state.pet.name)

    st.session_state.owner.name = owner_name
    if pet_name != st.session_state.pet.name:
        st.session_state.pet.name = pet_name

    if st.button("Add dog to owner"):
        new_pet = Pet(name=pet_name, species="dog")
        if not any(existing.name.lower() == new_pet.name.lower() for existing in st.session_state.owner.pets):
            st.session_state.owner.add_pet(new_pet)
        st.session_state.pet = new_pet
        st.success(f"Added {pet_name} to {st.session_state.owner.name}'s dogs.")

    st.divider()
    st.subheader("Add an appointment")
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Appointment", value="Vet Visit")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        task_time = st.time_input("Time", value=datetime.now().time())
        submitted = st.form_submit_button("Add appointment")
        if submitted:
            task = Task(
                description=task_title,
                duration_minutes=int(duration),
                priority=priority,
                time_of_day=task_time.strftime("%H:%M"),
                due_date=datetime.combine(datetime.now().date(), task_time),
            )
            st.session_state.pet.add_task(task)
            scheduler = Scheduler(st.session_state.owner, pet=st.session_state.pet)
            conflict_warning = scheduler.detect_conflicts(st.session_state.pet.tasks)
            if conflict_warning:
                st.warning(
                    f"⚠️ {st.session_state.pet.name} already has a task at this time. "
                    f"{conflict_warning} Please choose another time or review the schedule before confirming."
                )
            else:
                st.success(f"Added '{task_title}' for {st.session_state.pet.name} without conflicts.")

    st.divider()
    st.subheader("Scheduler overview")
    scheduler = Scheduler(st.session_state.owner, pet=st.session_state.pet)
    pet_filter = st.selectbox(
        "View appointments for",
        ["All dogs"] + [pet.name for pet in st.session_state.owner.pets],
    )
    all_tasks = st.session_state.owner.get_all_tasks()
    if pet_filter == "All dogs":
        visible_tasks = scheduler.filter_tasks(all_tasks, completed=False)
    else:
        visible_tasks = scheduler.filter_tasks(all_tasks, completed=False, pet_name=pet_filter)
    sorted_tasks = scheduler.sort_by_time(visible_tasks)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Appointments", len(sorted_tasks))
    col_b.metric("Dogs", len(st.session_state.owner.pets))
    conflict_warning = scheduler.detect_conflicts(sorted_tasks)
    col_c.metric("Conflicts", 1 if conflict_warning else 0)

    chart_data = {pet.name: len(pet.get_pending_tasks()) for pet in st.session_state.owner.pets}
    if chart_data:
        st.caption("Appointments by dog")
        st.bar_chart(chart_data)

    if sorted_tasks:
        schedule_rows = []
        for task in sorted_tasks:
            matching_pet = next(
                (pet for pet in st.session_state.owner.pets if task in pet.tasks),
                st.session_state.pet,
            )
            schedule_rows.append(
                {
                    "Dog": matching_pet.name,
                    "Appointment": task.description,
                    "Time": task.time_of_day or "Not set",
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority.title(),
                }
            )
        st.caption("Upcoming appointments in sorted order")
        st.dataframe(schedule_rows, use_container_width=True)
    else:
        st.info("No upcoming appointments yet. Add one above to build the schedule.")

    if conflict_warning:
        st.warning(conflict_warning)
    else:
        st.success("No scheduling conflicts found for the selected view.")


def render_ai_guide_tab() -> None:
    """Render the retrieval-augmented dog-care guide."""
    initialize_schedule_state()
    st.subheader("AI Dog Care Guide")
    st.write("Ask about feeding, food safety, exercise, bathing, grooming, dental care, or enrichment.")

    if "ai_profiles" not in st.session_state:
        st.session_state.ai_profiles = {}

    dog_names = [pet.name for pet in st.session_state.owner.pets]
    selected_dog = st.selectbox(
        "Select dog for this question",
        dog_names or ["Mochi"],
        index=dog_names.index(st.session_state.pet.name) if st.session_state.pet.name in dog_names else 0,
    )
    profile_values = st.session_state.ai_profiles.get(selected_dog, {})

    with st.expander("Dog profile", expanded=True):
        dog_name = st.text_input(
            "Name",
            value=profile_values.get("name", selected_dog),
            key=f"ai_dog_name_{selected_dog}",
        )
        life_stage_options = ["Puppy", "Adult", "Senior"]
        life_stage_default = profile_values.get("life stage", "Adult")
        life_stage = st.selectbox(
            "Life stage",
            life_stage_options,
            index=life_stage_options.index(life_stage_default) if life_stage_default in life_stage_options else 1,
            key=f"ai_life_stage_{selected_dog}",
        )
        breed = st.text_input(
            "Breed (optional)",
            value=profile_values.get("breed", ""),
            key=f"ai_breed_{selected_dog}",
        )
        size_options = ["Small", "Medium", "Large"]
        size_default = profile_values.get("size", "Medium")
        size = st.selectbox(
            "Size",
            size_options,
            index=size_options.index(size_default) if size_default in size_options else 1,
            key=f"ai_size_{selected_dog}",
        )
        activity_options = ["Low", "Moderate", "High"]
        activity_default = profile_values.get("activity level", "Moderate")
        activity = st.selectbox(
            "Activity level",
            activity_options,
            index=activity_options.index(activity_default) if activity_default in activity_options else 1,
            key=f"ai_activity_{selected_dog}",
        )
        health_notes = st.text_input(
            "Health notes (optional)",
            value=profile_values.get("health notes", ""),
            key=f"ai_health_notes_{selected_dog}",
        )

    question = st.text_area(
        "Your question",
        placeholder="How much exercise does my senior dog need?",
        key="ai_question",
    )
    if st.button("Ask PawPal+", type="primary"):
        profile = {
            "name": dog_name,
            "life stage": life_stage,
            "breed": breed,
            "size": size,
            "activity level": activity,
            "health notes": health_notes,
        }
        st.session_state.ai_profiles[selected_dog] = profile
        with st.spinner("Retrieving dog-care guidance..."):
            result = answer_question(question, profile)

        if result["status"] == "ok":
            st.success(result["answer"])
        elif result["status"] in {"emergency", "medication_safety", "generation_error"}:
            st.error(result["answer"])
        else:
            st.warning(result["answer"])

        if result["sources"]:
            st.markdown("**Sources used**")
            for source in result["sources"]:
                st.markdown(f'- [{source["title"]}]({source["url"]})')

    st.divider()
    st.caption("General educational information only. PawPal+ does not diagnose, prescribe, or replace veterinary care.")


schedule_tab, ai_tab = st.tabs(["Care Schedule", "AI Dog Care Guide"])
with schedule_tab:
    render_schedule_tab()
with ai_tab:
    render_ai_guide_tab()
