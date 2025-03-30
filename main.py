import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from utils.sports_data import get_live_games
from utils.ai_summary import generate_game_summary
from utils.notifications import subscribe_to_updates
from utils.stats import (
    generate_team_stats,
    create_score_timeline,
    create_hitting_comparison,
    create_pitching_comparison,
    create_box_score
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MLB Live Dashboard",
    page_icon="⚾",
    layout="wide"
)

# Load custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_game_tile(game, idx):
    """Helper function to display a single game tile"""
    # Get team codes (first 3 letters of team name)
    home_code = game['home_team'][:3].upper()
    away_code = game['away_team'][:3].upper()
    
    # Initialize session state for this game if it doesn't exist
    if f"selected_game_{idx}" not in st.session_state:
        st.session_state[f"selected_game_{idx}"] = False
    
    # Define the tile style
    tile_style = """
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    """
    
    # Create a container for the tile
    with st.container():
        # Create a clickable tile
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"<div style='text-align: center'><span style='font-weight: bold; font-size: 1.2em;'>{home_code}</span><br><span style='font-size: 0.8em; color: #666;'>{game['home_team']}</span></div>", unsafe_allow_html=True)
        
        with col2:
            # Display score
            st.markdown(f"<div style='text-align: center; font-size: 1.8em; font-weight: bold;'>{game['home_score']} - {game['away_score']}</div>", unsafe_allow_html=True)
            # Display status
            status_color = "#e74c3c" if game['status'] == "Live" else "#3498db" if game['status'] == "Upcoming" else "#2ecc71"
            status_bg_color = "rgba(231, 76, 60, 0.1)" if game['status'] == "Live" else "rgba(52, 152, 219, 0.1)" if game['status'] == "Upcoming" else "rgba(46, 204, 113, 0.1)"
            st.markdown(f"<div style='text-align: center'><span style='display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 500; background-color: {status_bg_color}; color: {status_color};'>{game['status']}</span></div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"<div style='text-align: center'><span style='font-weight: bold; font-size: 1.2em;'>{away_code}</span><br><span style='font-size: 0.8em; color: #666;'>{game['away_team']}</span></div>", unsafe_allow_html=True)
        
        # Add a clickable button
        if st.button("View Details", key=f"tile_{idx}"):
            st.session_state[f"selected_game_{idx}"] = not st.session_state[f"selected_game_{idx}"]
            st.session_state['selected_game'] = game if st.session_state[f"selected_game_{idx}"] else None

def display_game_details(game):
    """Display detailed information for a selected game"""
    st.subheader(f"{game['away_team']} vs {game['home_team']}")
    
    # Display game summary and highlight videos
    if game['status'] == "Finished":
        # Get game summary
        summary = generate_game_summary(game)
        st.write(summary)
        
        # Display highlight videos if available
        if game.get('highlights'):
            st.subheader("Game Highlights")
            for highlight in game['highlights']:
                st.write(f"**{highlight['description']}**")
                if highlight.get('timestamp'):
                    st.write(f"Time: {highlight['timestamp']}")
    
    # Display advanced statistics
    st.subheader("Advanced Statistics")
    
    # Create tabs for different stat views
    tab1, tab2, tab3 = st.tabs(["Game Flow", "Hitting Stats", "Pitching Stats"])
    
    with tab1:
        # Generate and display score timeline
        timeline = create_score_timeline(game)
        if timeline:
            st.plotly_chart(timeline, use_container_width=True)
    
    with tab2:
        # Generate and display hitting comparison
        stats = generate_team_stats(game)
        if stats:
            hitting_comparison = create_hitting_comparison(stats, game['home_team'], game['away_team'])
            if hitting_comparison:
                st.plotly_chart(hitting_comparison, use_container_width=True)
    
    with tab3:
        # Generate and display pitching comparison
        stats = generate_team_stats(game)
        if stats:
            pitching_comparison = create_pitching_comparison(stats, game['home_team'], game['away_team'])
            if pitching_comparison:
                st.plotly_chart(pitching_comparison, use_container_width=True)
    
    # Display box score if available
    if game.get('player_stats'):
        st.subheader("Box Score")
        
        # Create box score tables
        home_hitting_df, home_pitching_df, away_hitting_df, away_pitching_df = create_box_score(game)
        
        # Display hitting stats
        st.write("Hitting")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{game['home_team']}**")
            if not home_hitting_df.empty:
                st.dataframe(home_hitting_df, use_container_width=True)
        with col2:
            st.write(f"**{game['away_team']}**")
            if not away_hitting_df.empty:
                st.dataframe(away_hitting_df, use_container_width=True)
        
        # Display pitching stats
        st.write("Pitching")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{game['home_team']}**")
            if not home_pitching_df.empty:
                st.dataframe(home_pitching_df, use_container_width=True)
        with col2:
            st.write(f"**{game['away_team']}**")
            if not away_pitching_df.empty:
                st.dataframe(away_pitching_df, use_container_width=True)

def pre_cache_games():
    """Pre-cache games for yesterday, today, and tomorrow"""
    today = datetime.now().date()
    
    # Cache yesterday's completed games
    yesterday = today - timedelta(days=1)
    get_live_games(["MLB"], "Finished", yesterday)
    
    # Cache today's games
    get_live_games(["MLB"], "All", today)
    
    # Cache tomorrow's upcoming games
    tomorrow = today + timedelta(days=1)
    get_live_games(["MLB"], "Upcoming", tomorrow)

def main():
    # Pre-cache games when the application starts
    pre_cache_games()
    
    # Title section
    st.title("⚾ MLB Live Dashboard")
    
    # User parameters section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date(),
            min_value=datetime.now().date() - timedelta(days=1),
            max_value=datetime.now().date() + timedelta(days=1)
        )
    
    with col2:
        status_filter = st.selectbox(
            "Game Status",
            ["All", "Live", "Upcoming", "Finished"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Start Time", "Score"]
        )
    
    # Get live games data
    with st.spinner(f'Fetching MLB games for {selected_date.strftime("%Y-%m-%d")}...'):
        games = get_live_games(["MLB"], status_filter, selected_date)
        
        if not games:
            st.warning(f"No games found for {selected_date.strftime('%Y-%m-%d')}.")
        else:
            st.success(f"Found {len(games)} games for {selected_date.strftime('%Y-%m-%d')}")
    
    # Sort games
    if sort_by == "Score":
        games.sort(key=lambda x: (x['home_score'] + x['away_score']), reverse=True)
    else:  # Start Time
        games.sort(key=lambda x: x['time'])
    
    # Organize games by status
    live_games = [g for g in games if g['status'] == "Live"]
    upcoming_games = [g for g in games if g['status'] == "Upcoming"]
    finished_games = [g for g in games if g['status'] == "Finished"]
    
    # Initialize selected game in session state if not exists
    if 'selected_game' not in st.session_state:
        st.session_state['selected_game'] = None
    
    # Display games in a grid layout
    st.markdown("### Games")
    
    # Create a grid of game tiles
    for status, game_list in [("Live", live_games), ("Upcoming", upcoming_games), ("Finished", finished_games)]:
        if game_list:
            st.markdown(f"#### {status} Games")
            
            # Create rows with 3 columns each
            rows = (len(game_list) + 2) // 3
            for row in range(rows):
                # Create a row with 3 columns
                cols = st.columns(3)
                for col in range(3):
                    idx = row * 3 + col
                    if idx < len(game_list):
                        with cols[col]:
                            display_game_tile(game_list[idx], idx)
    
    # Display game details in the bottom panel
    if st.session_state['selected_game']:
        display_game_details(st.session_state['selected_game'])
    
    # Auto-refresh for today's date
    if selected_date == datetime.now().date():
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()