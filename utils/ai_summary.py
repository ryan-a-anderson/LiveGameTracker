import os
import google.generativeai as genai
from datetime import datetime
from typing import Dict, Any

def generate_game_summary(game):
    """Generate a concise summary of the game using Gemini API"""
    print("\n=== Raw Game Data ===")
    print(game)
    
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare game data
    league = game['league']
    home_team = game['home_team']
    away_team = game['away_team']
    home_score = game['home_score']
    away_score = game['away_score']
    status = game['status']
    date = game.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Format player statistics
    player_stats_text = ""
    if 'player_stats' in game:
        print("\n=== Player Stats ===")
        print(game['player_stats'])
        for team_type in ['home', 'away']:
            team_name = home_team if team_type == 'home' else away_team
            if team_name in game['player_stats']:
                player_stats_text += f"\n{team_name} Players:\n"
                for player in game['player_stats'][team_name]:
                    stats = []
                    # Add batting stats
                    if player.get('hits', 0) > 0:
                        stats.append(f"{player['hits']} hits")
                    if player.get('runs', 0) > 0:
                        stats.append(f"{player['runs']} runs")
                    if player.get('rbi', 0) > 0:
                        stats.append(f"{player['rbi']} RBI")
                    if player.get('homeRuns', 0) > 0:
                        stats.append(f"{player['homeRuns']} HR")
                    
                    # Add pitching stats
                    if player.get('strikeouts', 0) > 0:
                        stats.append(f"{player['strikeouts']} K")
                    if player.get('innings_pitched', '0.0') != '0.0':
                        stats.append(f"{player['innings_pitched']} IP")
                    if player.get('earned_runs', 0) > 0:
                        stats.append(f"{player['earned_runs']} ER")
                    if player.get('walks', 0) > 0:
                        stats.append(f"{player['walks']} BB")
                    
                    if stats:
                        player_stats_text += f"- {player['name']}: {', '.join(stats)}\n"
    
    # Format highlights
    highlights_text = ""
    if 'highlights' in game and game['highlights']:
        print("\n=== Highlights ===")
        print(game['highlights'])
        highlights_text = "\nKey Moments:\n"
        for highlight in game['highlights']:
            highlights_text += f"- {highlight['description']} ({highlight['timestamp']})\n"
    
    # Get team season stats for upcoming games
    team_stats_text = ""
    if status == "Upcoming" and 'team_stats' in game:
        print("\n=== Team Stats ===")
        print(game['team_stats'])
        team_stats = game['team_stats']
        team_stats_text = "\n2024 Season Stats:\n"
        
        # Add home team stats
        if f"{home_team}_2024_hitting" in team_stats:
            hitting = team_stats[f"{home_team}_2024_hitting"]
            pitching = team_stats[f"{home_team}_2024_pitching"]
            team_stats_text += f"\n{home_team}:\n"
            team_stats_text += f"- Hitting: {hitting['runs']} runs/game, {hitting['homeRuns']} HR, {hitting['battingAvg']} AVG\n"
            team_stats_text += f"- Pitching: {pitching['era']} ERA, {pitching['wins']}-{pitching['losses']} W-L\n"
        
        # Add away team stats
        if f"{away_team}_2024_hitting" in team_stats:
            hitting = team_stats[f"{away_team}_2024_hitting"]
            pitching = team_stats[f"{away_team}_2024_pitching"]
            team_stats_text += f"\n{away_team}:\n"
            team_stats_text += f"- Hitting: {hitting['runs']} runs/game, {hitting['homeRuns']} HR, {hitting['battingAvg']} AVG\n"
            team_stats_text += f"- Pitching: {pitching['era']} ERA, {pitching['wins']}-{pitching['losses']} W-L\n"
    
    # Get 2025 season stats if available
    if 'team_stats' in game:
        team_stats = game['team_stats']
        team_stats_text += "\n2025 Season Stats:\n"
        
        # Add home team stats
        if f"{home_team}_2025_hitting" in team_stats:
            hitting = team_stats[f"{home_team}_2025_hitting"]
            pitching = team_stats[f"{home_team}_2025_pitching"]
            team_stats_text += f"\n{home_team}:\n"
            team_stats_text += f"- Hitting: {hitting['runs']} runs/game, {hitting['homeRuns']} HR, {hitting['battingAvg']} AVG\n"
            team_stats_text += f"- Pitching: {pitching['era']} ERA, {pitching['wins']}-{pitching['losses']} W-L\n"
        
        # Add away team stats
        if f"{away_team}_2025_hitting" in team_stats:
            hitting = team_stats[f"{away_team}_2025_hitting"]
            pitching = team_stats[f"{away_team}_2025_pitching"]
            team_stats_text += f"\n{away_team}:\n"
            team_stats_text += f"- Hitting: {hitting['runs']} runs/game, {hitting['homeRuns']} HR, {hitting['battingAvg']} AVG\n"
            team_stats_text += f"- Pitching: {pitching['era']} ERA, {pitching['wins']}-{pitching['losses']} W-L\n"
    
    # Get pitching decisions
    pitching_decisions = ""
    if status == "Finished":
        if game.get('winning_pitcher'):
            pitching_decisions += f"\nWinning Pitcher: {game['winning_pitcher']}"
        if game.get('losing_pitcher'):
            pitching_decisions += f"\nLosing Pitcher: {game['losing_pitcher']}"
        if game.get('save_pitcher'):
            pitching_decisions += f"\nSave: {game['save_pitcher']}"
    
    # Create the prompt based on game status
    if status == "Upcoming":
        prompt = f"""
        Generate a concise summary for this upcoming MLB game:
        
        Game: {away_team} @ {home_team}
        Date: {date}
        Time: {game['time']}
        
        Team Statistics:
        {team_stats_text}
        
        Please provide a brief preview focusing on:
        1. Key storylines and matchups
        2. Recent team performance
        3. Notable players to watch
        4. Pitching matchup analysis
        
        Keep the summary concise and engaging.
        """
    else:
        prompt = f"""
        Generate a concise summary for this MLB game:
        
        Game: {away_team} @ {home_team}
        Date: {date}
        Final Score: {home_team} {home_score} - {away_score} {away_team}
        
        Player Statistics:
        {player_stats_text}
        
        Pitching Decisions:
        {pitching_decisions}
        
        Key Moments:
        {highlights_text}
        
        Please provide a summary that includes:
        1. How the game was won (key plays, turning points)
        2. Notable individual performances (both hitting and pitching)
        3. Pitching performances and decisions
        4. Any records or milestones achieved
        
        Keep the summary concise but informative.
        """
    
    print("\n=== Formatted Prompt ===")
    print(prompt)
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
        
        # Add timestamp to the summary
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"Generated at {timestamp}\n\n{summary}"
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return f"Error generating summary. Please try again later."