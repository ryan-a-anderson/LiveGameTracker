import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
import json

# Load local modules
from utils.sports_data import get_live_games, pre_cache_games, get_mlb_games
from utils.stats import create_box_score, calculate_team_stats
from utils.ai_summary import generate_game_summary

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Set page config
st.set_page_config(
    page_title="MLB Live Game Tracker",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Pre-cache games for faster loading
pre_cache_games()

def display_game_details(game):
    # Create columns for team names and scores
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.subheader(f"{game['away_team']} - {game['away_score']}")
    
    with col2:
        if game['status'] == "Live":
            st.subheader(f"{game['period']} {game['game_clock']}")
        elif game['status'] == "Upcoming":
            st.subheader(f"Today {game['time']}")
        else:
            st.subheader("Final")
    
    with col3:
        st.subheader(f"{game['home_team']} - {game['home_score']}")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Game Summary", "Box Score", "Team Stats"])
    
    with tab1:
        # If the game is finished, generate a summary
        if game['status'] == "Finished":
            if st.button("Generate Summary", key=f"summary_{game['id']}"):
                with st.spinner("Generating game summary..."):
                    summary = generate_game_summary(game)
                    st.markdown(summary)
                    
                    # Show decisions if available
                    if game.get('winning_pitcher') and game.get('losing_pitcher'):
                        st.markdown("### Pitching Decisions")
                        st.markdown(f"**W**: {game['winning_pitcher']}")
                        st.markdown(f"**L**: {game['losing_pitcher']}")
                        if game.get('save_pitcher'):
                            st.markdown(f"**S**: {game['save_pitcher']}")
        else:
            st.info("Game summary will be available when the game is finished.")
    
    with tab2:
        # Display box score if game is finished or in progress
        if game['status'] in ["Finished", "Live"]:
            # Generate box score
            home_hitting, home_pitching, away_hitting, away_pitching = create_box_score(game)
            
            # Create columns for home and away teams
            col1, col2 = st.columns(2)
            
            with col1:
                # Away team box scores
                st.markdown(f"### {game['away_team']} Hitting")
                if away_hitting is not None and not away_hitting.empty:
                    st.dataframe(away_hitting, use_container_width=True)
                else:
                    st.info("No hitting data available.")
                
                st.markdown(f"### {game['away_team']} Pitching")
                if away_pitching is not None and not away_pitching.empty:
                    st.dataframe(away_pitching, use_container_width=True)
                else:
                    st.info("No pitching data available.")
            
            with col2:
                # Home team box scores
                st.markdown(f"### {game['home_team']} Hitting")
                if home_hitting is not None and not home_hitting.empty:
                    st.dataframe(home_hitting, use_container_width=True)
                else:
                    st.info("No hitting data available.")
                
                st.markdown(f"### {game['home_team']} Pitching")
                if home_pitching is not None and not home_pitching.empty:
                    st.dataframe(home_pitching, use_container_width=True)
                else:
                    st.info("No pitching data available.")
        else:
            st.info("Box score will be available when the game starts.")
    
    with tab3:
        # Display team statistics
        if 'team_stats' in game and game['team_stats']:
            home_stats, away_stats = calculate_team_stats(game)
            
            # Create columns for home and away teams
            col1, col2 = st.columns(2)
            
            with col1:
                # Away team stats
                st.markdown(f"### {game['away_team']} Team Stats")
                if away_stats is not None and not away_stats.empty:
                    st.dataframe(away_stats, use_container_width=True)
                else:
                    st.info("No team stats available.")
            
            with col2:
                # Home team stats
                st.markdown(f"### {game['home_team']} Team Stats")
                if home_stats is not None and not home_stats.empty:
                    st.dataframe(home_stats, use_container_width=True)
                else:
                    st.info("No team stats available.")
        else:
            st.info("Team stats will be available when the game starts.")

def main():
    st.title("⚾ MLB Live Game Tracker")
    
    # Create sidebar for filtering options
    with st.sidebar:
        st.header("Filter Options")
        
        # Allow user to select game status
        status_options = ["All", "Live", "Upcoming", "Finished"]
        selected_status = st.selectbox("Game Status", status_options)
        
        # Allow user to select date
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        date_options = {
            "Yesterday": yesterday,
            "Today": today,
            "Tomorrow": tomorrow
        }
        
        selected_date_str = st.selectbox("Date", list(date_options.keys()))
        selected_date = date_options[selected_date_str]
        
        # Add a refresh button
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # Get live games based on selections
    with st.spinner("Loading games..."):
        games = get_live_games(selected_status, selected_date)
    
    # Display games
    if not games:
        st.info(f"No MLB games found for {selected_date_str} with status: {selected_status}")
    else:
        # Create a card for each game
        for i, game in enumerate(games):
            with st.container(border=True):
                display_game_details(game)
            
            # Add spacing between games
            if i < len(games) - 1:
                st.markdown("---")

if __name__ == "__main__":
    main()