import streamlit as st # type: ignore
import datetime
import json
import os

DATA_FILE = "recovery_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Restoring streaks
            st.session_state.streak = data.get('streak', 0)
            # Restore last_checkin (converts string back to date)
            last_str = data.get('last_checkin')
            st.session_state.last_checkin = datetime.date.fromisoformat(last_str) if last_str else None
            # Restores journal
            st.session_state.journal = data.get('journal', [])

    else:
        # For first time - set to defaults
        st.session_state.streak = 0
        st.session_state.last_checkin = None
        st.session_state.journal = []

def save_data():
    data = {
        'streak' : st.session_state.streak,
        'last_checkin' : st.session_state.last_checkin.isoformat() if st.session_state.last_checkin else None,
        'journal' : st.session_state.journal
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

st.set_page_config(
    page_title="Recovery",
    page_icon="🥹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

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
    st.write("Track your sobriety, journel your thoughts, talk with others.")
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
        save_data()


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
            save_data()
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
            for item in entries_to_show:
                st.write(f"**{item['date']}**: {item['text']}")

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