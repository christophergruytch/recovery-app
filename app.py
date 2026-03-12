import streamlit as st # type: ignore
import datetime
import json
import os

if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None
if 'journal' not in st.session_state:
    st.session_state.journal = []
if 'motivation' not in st.session_state:
    st.session_state.motivation = 5

st.set_page_config(
    page_title="Recovery",
    page_icon="🥹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

page = st.sidebar.radio(
    label="Menu",
    options=["🏠 Home", "✅ Daily Check-In", "📓 Journal", "🎙️ Let's All Talk", "📊 Progress", "🆘 Resources", "⚙️ Settings"],
    index=0,     # starts at Home
    key="nav_menu"
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="manifest.json">
""", unsafe_allow_html=True)


if page=="🏠 Home":
    st.title("Welcome to Recovery")
    st.write("Our mission is to...")
    st.metric("Current Streak", st.session_state.get('streak', 0), "days")
    st.session_state.motivation = st.slider("How motivated are you today?", 1, 10)
    st.write(f"Your motivation: {st.session_state.motivation}")

elif page=="✅ Daily Check-In":
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    if 'last_checkin' not in st.session_state:
        st.session_state.last_checkin = None

    st.header("Daily Check-In") #subheader

    if st.button("Check In Today"):
        today = datetime.date.today() # for testing: datetime.date(2025, 10, 1), for real: datetime.date.today()
        if st.session_state.last_checkin == today:
            st.warning("You have already checked in today")
        else:
            if st.session_state.last_checkin is None:
                st.success("You have strated a new streak!")
                st.session_state.last_checkin = today
                st.session_state.streak += 1
            else:
                delta = today - st.session_state.last_checkin
                if delta.days == 1:
                    st.success("You've added another day!")
                    st.session_state.last_checkin = today
                    st.session_state.streak += 1
                else:
                    st.warning(f"You have missed {delta.days - 1} day(s). Streak is reset to 1. Don't worry, we are here on this journey with you!")
                    # st.warning(f"Delta is above 1, delta = {delta}, today = {today}, last_checkin = {st.session_state.last_checkin}") this is for testing purposes.")
                    st.session_state.last_checkin = today
                    st.session_state.streak = 1
        


    st.write(f"Today: {datetime.date.today()}")
    st.write(f"Today: {st.session_state.streak}")

    st.metric("Current Streak", st.session_state.streak, "days")

elif page=="📓 Journal":

        st.header("Journal Your Thoughts")

        entry = st.text_area("What's on your mind today?")

        if st.button("Save Entry"):
            if 'journal' not in st.session_state:
                st.session_state.journal = []
            st.session_state.journal.append({
                "date": str(datetime.date.today()),
                "text": entry
            })
            st.success("Entry Saved!")


        st.header("Journal Entries")

        if 'journal' not in st.session_state:
            st.session_state.journal = []           # just in case it's missing

        if not st.session_state.journal:
            st.info("No journal entries yet. Add one above!")
        else:
            # Use session_state for the toggle (persists across reruns)
            if 'show_all_journal' not in st.session_state:
                st.session_state.show_all_journal = False  # start collapsed

            # Decide how many to show
            if st.session_state.show_all_journal:
                entries_to_show = st.session_state.journal
                button_label = "Show less"
            else:
                entries_to_show = st.session_state.journal[-3:]   # last 3
                button_label = "Show more"

            # Show the selected entries
            for index, item in enumerate(entries_to_show):
                col_text, col_edit, col_delete = st.columns([8, 1, 1])

                with col_text:
                    st.write(f"**{item['date']}**: {item['text']}")

                with col_edit:
                    if st.button("✏️", key=f"edit_{index}_{item.get('date', '')}", help="Edit this entry"):
                        st.info("Edit feature coming soon...")

                with col_delete:
                    if st.button("🗑️", key=f"delete_{index}_{item.get('date', '')}", help="Delete this entry"):
                        full_journal = st.session_state.journal

                        if st.session_state.show_all_journal:
                            real_index = index
                        else:
                            real_index = len(full_journal) - len(entries_to_show) + index
                        
                        del full_journal[real_index]
                        st.success("Entry deleted.")
                        st.rerun()  #refreshes the page instantly

            # The toggle button
            if st.button(button_label):
                # Flip the state — this will trigger rerun automatically
                st.session_state.show_all_journal = not st.session_state.show_all_journal
                st.rerun()

elif page=="🎙️ Let's All Talk":
    st.write("Where you can talk with others will go here.")

elif page=="📊 Progress":
    st.write("Your progress will go here.")

elif page=="🆘 Resources":
    st.write("Resources to help will go here.")

elif page=="⚙️ Settings":
    st.write("Settings will go here.")