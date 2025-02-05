import streamlit as st
import time
from datetime import datetime
import pandas as pd
from utils.sports_data import get_live_games
from utils.ai_summary import generate_game_summary
from utils.notifications import subscribe_to_updates
from utils.stats import (
    generate_team_stats,
    create_possession_chart,
    create_shots_comparison,
    create_score_timeline,
    create_pass_accuracy_gauge
)

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
        with st.expander(f"{game['league']} - {game['home_team']} vs {game['away_team']}", expanded=False):
            # Main game info
            cols = st.columns([3, 1])

            with cols[0]:
                st.markdown(
                    f"""
                    <div class="score-container">
                        <span class="league-badge league-{game['league'].split()[0]}">{game['league']}</span>
                        <span class="status-indicator status-{game['status']}">{game['status']}</span>
                        <span class="team">{game['home_team']}</span>
                        <span class="score">{game['home_score']} - {game['away_score']}</span>
                        <span class="team">{game['away_team']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with cols[1]:
                if st.button(f"Subscribe 🔔", key=f"subscribe_{idx}"):
                    st.info("Subscriptions are currently disabled")

            # Game Summary Section
            if 'show_summary_' + str(idx) not in st.session_state:
                st.session_state['show_summary_' + str(idx)] = False

            if st.button("Show Game Summary", key=f"summary_btn_{idx}"):
                st.session_state['show_summary_' + str(idx)] = not st.session_state['show_summary_' + str(idx)]

            if st.session_state['show_summary_' + str(idx)]:
                summary = generate_game_summary(game)
                st.markdown(summary)

                # Display highlight videos if available
                if game.get('highlights'):
                    st.subheader("🎥 Game Highlights")
                    for highlight in game['highlights']:
                        with st.container():
                            st.markdown(f"""
                            🕒 {highlight['timestamp']} - **{highlight['title']}**  
                            _{highlight['description']}_
                            """)
                            # In production, this would be a real video player
                            st.info("Video player placeholder - In production, this would show the actual highlight video")

                # Advanced Statistics Section
                st.subheader("📊 Advanced Statistics")

                # Generate mock statistics
                stats = generate_team_stats(game)

                # Create tabs for different statistics views
                tab1, tab2, tab3 = st.tabs(["Game Flow", "Team Comparison", "Pass Analysis"])

                with tab1:
                    # Score Timeline
                    st.plotly_chart(create_score_timeline(game), use_container_width=True)

                with tab2:
                    # Create two columns for possession and shots
                    stat_col1, stat_col2 = st.columns(2)

                    with stat_col1:
                        # Possession pie chart
                        st.plotly_chart(
                            create_possession_chart(
                                stats, 
                                game['home_team'], 
                                game['away_team']
                            ),
                            use_container_width=True
                        )

                    with stat_col2:
                        # Shots comparison
                        st.plotly_chart(
                            create_shots_comparison(
                                stats,
                                game['home_team'],
                                game['away_team']
                            ),
                            use_container_width=True
                        )

                with tab3:
                    # Pass accuracy gauges
                    pass_col1, pass_col2 = st.columns(2)

                    with pass_col1:
                        st.plotly_chart(
                            create_pass_accuracy_gauge(
                                game['home_team'],
                                stats['pass_accuracy'][game['home_team']]
                            ),
                            use_container_width=True
                        )

                    with pass_col2:
                        st.plotly_chart(
                            create_pass_accuracy_gauge(
                                game['away_team'],
                                stats['pass_accuracy'][game['away_team']]
                            ),
                            use_container_width=True
                        )

    # Auto-refresh every 30 seconds
    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()