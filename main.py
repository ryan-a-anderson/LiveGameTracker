import streamlit as st
import time
from datetime import datetime
import pandas as pd
from utils.sports_data import get_live_games
from utils.ai_summary import generate_game_summary
from utils.notifications import subscribe_to_updates

# Page configuration
st.set_page_config(
    page_title="Live Sports Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Load custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("🏆 Live Sports Dashboard")

    # League selection
    leagues = ["NFL", "NBA", "MLB", "Premier League"]
    selected_leagues = st.multiselect(
        "Select Leagues to Follow",
        leagues,
        default=leagues
    )

    # Create columns for filters
    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Game Status",
            ["All", "Live", "Upcoming", "Finished"]
        )

    with col2:
        sort_by = st.selectbox(
            "Sort By",
            ["Start Time", "League", "Score"]
        )

    # Display live games
    st.subheader("Live Games")

    # Get live games data
    games = get_live_games(selected_leagues, status_filter)

    # Display games in a grid
    for idx, game in enumerate(games):
        with st.container():
            col1, col2, col3 = st.columns([2,3,1])

            with col1:
                st.markdown(f"**{game['league']}**")
                st.text(f"🕒 {game['time']}")

            with col2:
                st.markdown(
                    f"""
                    <div class="score-container">
                        <span class="team">{game['home_team']}</span>
                        <span class="score">{game['home_score']} - {game['away_score']}</span>
                        <span class="team">{game['away_team']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                if st.button(f"Get Summary", key=f"summary_{idx}"):
                    summary = generate_game_summary(game)
                    st.json(summary)

                if st.button(f"Subscribe 🔔", key=f"subscribe_{idx}"):
                    st.info("Subscriptions are currently disabled")

    # Auto-refresh every 30 seconds (reduced from 5 minutes for testing)
    time.sleep(30)
    st.experimental_rerun()

if __name__ == "__main__":
    main()