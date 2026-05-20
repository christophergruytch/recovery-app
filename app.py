import streamlit as st # type: ignore
import datetime
import json
import os
import pandas as pd # type: ignore
from streamlit_javascript import st_javascript # type: ignore

if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'last_checkin' not in st.session_state:
    st.session_state.last_checkin = None
if 'journal' not in st.session_state:
    st.session_state.journal = []
if 'sobriety_start' not in st.session_state:
    st.session_state.sobriety_start = None
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'nickname' not in st.session_state:
    st.session_state.nickname = None
if 'longest_streak' not in st.session_state:
    st.session_state.longest_streak = 0
if 'longest_sobriety' not in st.session_state:
    st.session_state.longest_sobriety = 0


def get_storage_key(base_key: str) -> str:
    """Creates private key for each user"""
    if st.session_state.get('nickname'):
        return f"recovery_{base_key}_{st.session_state.nickname}"
    return f"recovery_{base_key}_temp"

def save_core_data():
    """Save streak, last_checkin, and sobriety timer to localStorage"""
    if 'nickname' not in st.session_state or not st.session_state.nickname:
        return  # Don't save if no nickname is set yet

    streak_key = f"recovery_streak_{st.session_state.nickname}"
    last_key = f"recovery_last_checkin_{st.session_state.nickname}"
    sobriety_key = f"recovery_sobriety_start_{st.session_state.nickname}"

    st_javascript(f"localStorage.setItem('{streak_key}', '{st.session_state.get('streak', 0)}')")

    if st.session_state.get('last_checkin'):
        st_javascript(f"localStorage.setItem('{last_key}', '{st.session_state.last_checkin.isoformat()}')")
    else:
        st_javascript(f"localStorage.removeItem('{last_key}')")

    if st.session_state.get('sobriety_start'):
        st_javascript(f"localStorage.setItem('{sobriety_key}', '{st.session_state.sobriety_start.isoformat()}')")
    else:
        st_javascript(f"localStorage.removeItem('{sobriety_key}')")


st.set_page_config(
    page_title="Recovery",
    page_icon="🥹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

page = st.sidebar.radio(
    label="Menu",
    options=["🏠 Home", "✅ Daily Check-In", "📓 Journal", "🎙️ Let's All Talk", "📊 Progress", "🆘 Resources", "⚙️ Settings"],
    index=0,  # starts at Home
    key="nav_menu"
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="manifest.json">
""", unsafe_allow_html=True)





if page == "🏠 Home":
    st.title("Welcome to Recovery")
    st.write("Our mission is to support you on your journey toward freedom.")

    # Two columns for the two main metrics
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Current Streak",
            value=f"{st.session_state.get('streak', 0)} days"
        )

    with col2:
        if st.session_state.get('sobriety_start') is None:
            st.metric(
                label="Days Sober",
                value="Not set"
            )
        else:
            days_sober = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric(
                label="Days Sober",
                value=f"{days_sober} days"
            )

    st.write("---")

    # Sobriety Timer section
    st.subheader("⏱️ Sobriety Timer")

    if st.session_state.get('sobriety_start') is None:
        sobriety_date = st.date_input(
            "When did your current sobriety period begin?",
            value=datetime.date.today(),
            max_value=datetime.date.today(),
            key="sobriety_start_input"
        )
        if st.button("Start Sobriety Timer"):
            st.session_state.sobriety_start = sobriety_date
            st.success("Sobriety timer started! Keep going 💪")
            st.rerun()
    else:
        if st.button("I Relapsed Today", type="secondary"):
            st.session_state.sobriety_start = None
            st.warning("💔 Timer has been reset. You can set a new start date.")
            st.rerun()

elif page == "✅ Daily Check-In":

    st.header("Daily Check-In")

    if st.button("Check In Today", key="checkin_btn", type="primary", use_container_width=True):
        today = datetime.date.today()

        if st.session_state.last_checkin == today:
            st.warning("You have already checked in today")
        else:
            if st.session_state.last_checkin is None:
                st.success("You have started a new streak!")
                st.session_state.streak += 1
                st.session_state.last_checkin = today
            else:
                delta = today - st.session_state.last_checkin
                if delta.days == 1:
                    st.success("You've added another day!")
                    st.session_state.streak += 1
                    st.session_state.last_checkin = today
                else:
                    st.warning(f"You have missed {delta.days - 1} day(s). Streak is reset to 1. Don't worry, we are here on this journey with you!")
                    st.session_state.streak = 1
                    st.session_state.last_checkin = today

            st.rerun()

    st.metric("Current Streak", st.session_state.get('streak', 0), "days")
        

elif page=="📓 Journal":

        st.header("Journal Your Thoughts")

        # Clear All button
        if st.button("🗑️ Clear All Journal Entries", type="secondary"):
            st.session_state.journal = []
            st.success("All journal entries have been cleared.")
            st.rerun()

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

        if not st.session_state.get('journal'):
                st.info("No entries yet. Add one above.")
        else:
            for idx, item in enumerate(st.session_state.journal):
                col_text, col_edit, col_delete = st.columns([7, 1, 1])

                with col_text:
                    if st.session_state.get('editing_index') == idx:
                        # Edit mode
                        edited_text = st.text_area("Edit your entry", value=item["text"], key=f"edit_area_{idx}")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("💾 Save Changes", key=f"save_edit_{idx}"):
                                st.session_state.journal[idx]["text"] = edited_text.strip()
                                st.session_state.editing_index = None
                                st.success("✅ Entry updated!")
                                st.rerun()
                        with c2:
                            if st.button("Cancel", key=f"cancel_edit_{idx}"):
                                st.session_state.editing_index = None
                                st.rerun()
                    else:
                        st.write(f"**{item['date']}**: {item['text']}")

                with col_edit:
                    if st.session_state.get('editing_index') is None:
                        if st.button("✏️", key=f"edit_btn_{idx}"):
                            st.session_state.editing_index = idx
                            st.rerun()

                with col_delete:
                    if st.button("🗑️", key=f"delete_btn_{idx}"):
                        del st.session_state.journal[idx]
                        st.success("Entry deleted.")
                        st.rerun()

elif page=="🎙️ Let's All Talk":
    st.write("Where you can talk with others will go here.")

elif page == "📊 Progress":
    st.header("📊 Your Progress")

    # Current metrics side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Current Streak",
            value=f"{st.session_state.get('streak', 0)} days"
        )

    with col2:
        if st.session_state.get('sobriety_start') is None:
            st.metric(label="Current Days Sober", value="Not set")
        else:
            days_sober = (datetime.date.today() - st.session_state.sobriety_start).days
            st.metric(
                label="Current Days Sober",
                value=f"{days_sober} days"
            )

    st.write("---")

    # Personal Bests
    st.subheader("🏆 Personal Bests")
    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            label="Longest Streak",
            value=f"{st.session_state.get('longest_streak', 0)} days"
        )

    with col4:
        st.metric(
            label="Longest Sobriety Period",
            value=f"{st.session_state.get('longest_sobriety', 0)} days"
        )

    # Total journal entries
    total_journal = len(st.session_state.get('journal', []))
    st.metric("Total Journal Entries Written", total_journal)

    st.write("---")

    # Journaling Activity Chart
    st.subheader("📈 Journaling Activity")

    journal = st.session_state.get('journal', [])

    if journal:
        df = pd.DataFrame(journal)
        df['date'] = pd.to_datetime(df['date'])
        daily_entries = df.groupby('date').size().reset_index(name='entries')
        daily_entries = daily_entries.sort_values('date')

        st.line_chart(
            data=daily_entries,
            x='date',
            y='entries',
            use_container_width=True
        )
        st.caption("Number of journal entries you wrote each day")
    else:
        st.info("Start writing in your journal to see your activity chart here.")

elif page=="🆘 Resources":
    st.write("Resources to help will go here.")

elif page == "⚙️ Settings":
    st.header("⚙️ Settings - Make This Private To You!")

    if not st.session_state.get('nickname'):
        # No nickname set yet
        st.info("First time here? Let's create your private space.")
        new_nickname = st.text_input(
            "Choose a nickname (e.g. chris_burbank)",
            placeholder="john_doe",
            max_chars=30,
            key="nickname_input"
        )
        if st.button("✅ Save My Nickname & Start Fresh!"):
            if new_nickname.strip():
                clean_nickname = "".join(c for c in new_nickname.strip().lower() if c.isalnum() or c == "_")
                if clean_nickname:
                    st.session_state.nickname = clean_nickname
                    st_javascript(f'localStorage.setItem("recovery_nickname", "{clean_nickname}")')
                    st.success(f"Welcome, {clean_nickname}! Your data is now private to you!")
                    st.rerun()
                else:
                    st.error("Nickname must contain at least one letter or number.")
            else:
                st.warning("Please enter a nickname.")
    else:
        # Nickname already set
        st.success(f"Current nickname: **{st.session_state.nickname}**")
        st.caption("All your streak, journal, and future data is stored privately under this nickname.")

        if st.button("Change Nickname (this will start with fresh data)", key="change_nickname_btn"):
            st.session_state.nickname = None
            st_javascript('localStorage.removeItem("recovery_nickname")')
            st.rerun()