import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

def generate_team_stats(game):
    """
    Generate advanced statistics for MLB teams using real game data
    """
    try:
        stats = {
            'hitting': {
                game['home_team']: {
                    'hits': 0,
                    'runs': 0,
                    'home_runs': 0,
                    'strikeouts': 0,
                    'walks': 0,
                    'batting_avg': 0.0
                },
                game['away_team']: {
                    'hits': 0,
                    'runs': 0,
                    'home_runs': 0,
                    'strikeouts': 0,
                    'walks': 0,
                    'batting_avg': 0.0
                }
            },
            'pitching': {
                game['home_team']: {
                    'strikeouts': 0,
                    'walks': 0,
                    'hits_allowed': 0,
                    'earned_runs': 0,
                    'era': 0.0
                },
                game['away_team']: {
                    'strikeouts': 0,
                    'walks': 0,
                    'hits_allowed': 0,
                    'earned_runs': 0,
                    'era': 0.0
                }
            }
        }

        # Extract stats from player_stats if available
        if 'player_stats' in game:
            for team_type in ['home', 'away']:
                team_name = game['home_team'] if team_type == 'home' else game['away_team']
                if team_name in game['player_stats']:
                    for player in game['player_stats'][team_name]:
                        # Hitting stats
                        stats['hitting'][team_name]['hits'] += player.get('hits', 0)
                        stats['hitting'][team_name]['runs'] += player.get('runs', 0)
                        stats['hitting'][team_name]['home_runs'] += player.get('homeRuns', 0)
                        stats['hitting'][team_name]['strikeouts'] += player.get('strikeouts', 0)
                        stats['hitting'][team_name]['walks'] += player.get('walks', 0)
                        
                        # Pitching stats
                        stats['pitching'][team_name]['strikeouts'] += player.get('strikeouts', 0)
                        stats['pitching'][team_name]['walks'] += player.get('walks', 0)
                        stats['pitching'][team_name]['hits_allowed'] += player.get('hits_allowed', 0)
                        stats['pitching'][team_name]['earned_runs'] += player.get('earned_runs', 0)

        return stats
    except Exception as e:
        print(f"Error generating team stats: {str(e)}")
        return None

def create_hitting_comparison(stats, home_team, away_team):
    """
    Create a bar chart comparing hitting statistics
    """
    try:
        categories = ['Hits', 'Runs', 'Home Runs', 'Strikeouts', 'Walks']
        
        fig = go.Figure(data=[
            go.Bar(name=home_team,
                   x=categories,
                   y=[stats['hitting'][home_team]['hits'],
                      stats['hitting'][home_team]['runs'],
                      stats['hitting'][home_team]['home_runs'],
                      stats['hitting'][home_team]['strikeouts'],
                      stats['hitting'][home_team]['walks']],
                   marker_color='#2ecc71'),
            go.Bar(name=away_team,
                   x=categories,
                   y=[stats['hitting'][away_team]['hits'],
                      stats['hitting'][away_team]['runs'],
                      stats['hitting'][away_team]['home_runs'],
                      stats['hitting'][away_team]['strikeouts'],
                      stats['hitting'][away_team]['walks']],
                   marker_color='#e74c3c')
        ])

        fig.update_layout(
            title="Hitting Statistics Comparison",
            barmode='group',
            xaxis_title="Metric",
            yaxis_title="Count"
        )
        return fig
    except Exception as e:
        print(f"Error creating hitting comparison: {str(e)}")
        return None

def create_pitching_comparison(stats, home_team, away_team):
    """
    Create a bar chart comparing pitching statistics
    """
    try:
        categories = ['Strikeouts', 'Walks', 'Hits Allowed', 'Earned Runs']
        
        fig = go.Figure(data=[
            go.Bar(name=home_team,
                   x=categories,
                   y=[stats['pitching'][home_team]['strikeouts'],
                      stats['pitching'][home_team]['walks'],
                      stats['pitching'][home_team]['hits_allowed'],
                      stats['pitching'][home_team]['earned_runs']],
                   marker_color='#2ecc71'),
            go.Bar(name=away_team,
                   x=categories,
                   y=[stats['pitching'][away_team]['strikeouts'],
                      stats['pitching'][away_team]['walks'],
                      stats['pitching'][away_team]['hits_allowed'],
                      stats['pitching'][away_team]['earned_runs']],
                   marker_color='#e74c3c')
        ])

        fig.update_layout(
            title="Pitching Statistics Comparison",
            barmode='group',
            xaxis_title="Metric",
            yaxis_title="Count"
        )
        return fig
    except Exception as e:
        print(f"Error creating pitching comparison: {str(e)}")
        return None

def create_score_timeline(game):
    """
    Create a line chart showing score progression by inning
    """
    try:
        # Calculate innings (assuming 9 innings for simplicity)
        innings = list(range(1, 10))
        
        # Initialize timeline data
        timeline_data = {
            'inning': [0],
            f"{game['home_team']}_score": [0],
            f"{game['away_team']}_score": [0]
        }

        # For now, we'll distribute the final score across innings
        # In a real implementation, we'd use actual inning-by-inning data
        current_home = 0
        current_away = 0
        
        # Distribute runs across innings
        for inning in innings:
            if current_home < game['home_score']:
                current_home += 1
                timeline_data['inning'].append(inning)
                timeline_data[f"{game['home_team']}_score"].append(current_home)
                timeline_data[f"{game['away_team']}_score"].append(current_away)
            
            if current_away < game['away_score']:
                current_away += 1
                timeline_data['inning'].append(inning)
                timeline_data[f"{game['home_team']}_score"].append(current_home)
                timeline_data[f"{game['away_team']}_score"].append(current_away)

        # Convert to DataFrame and sort by inning
        df = pd.DataFrame(timeline_data).sort_values('inning')

        # Create the line chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['inning'],
            y=df[f"{game['home_team']}_score"],
            name=game['home_team'],
            line=dict(color="#2ecc71", width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df['inning'],
            y=df[f"{game['away_team']}_score"],
            name=game['away_team'],
            line=dict(color="#e74c3c", width=2)
        ))

        fig.update_layout(
            title="Score Progression by Inning",
            xaxis_title="Inning",
            yaxis_title="Runs",
            hovermode="x unified"
        )

        return fig
    except Exception as e:
        print(f"Error creating score timeline: {str(e)}")
        return None

def create_box_score(game):
    """
    Create separate box score tables for hitting and pitching
    """
    try:
        if 'player_stats' not in game:
            return None, None, None, None

        # Create DataFrames for each team
        home_hitting = []
        home_pitching = []
        away_hitting = []
        away_pitching = []

        # Process home team
        if game['home_team'] in game['player_stats']:
            for player in game['player_stats'][game['home_team']]:
                # Hitting stats
                if any(player.get(stat, 0) > 0 for stat in ['hits', 'runs', 'rbi', 'homeRuns', 'walks']):
                    home_hitting.append({
                        'Name': player['name'],
                        'H': player.get('hits', 0),
                        'R': player.get('runs', 0),
                        'RBI': player.get('rbi', 0),
                        'HR': player.get('homeRuns', 0),
                        'BB': player.get('walks', 0),
                        'K': player.get('strikeouts', 0)
                    })
                
                # Pitching stats
                if any(player.get(stat, 0) > 0 for stat in ['strikeouts', 'walks', 'hits_allowed', 'earned_runs', 'innings_pitched']):
                    home_pitching.append({
                        'Name': player['name'],
                        'IP': player.get('innings_pitched', '0.0'),
                        'H': player.get('hits_allowed', 0),
                        'R': player.get('earned_runs', 0),
                        'ER': player.get('earned_runs', 0),
                        'BB': player.get('walks', 0),
                        'K': player.get('strikeouts', 0)
                    })

        # Process away team
        if game['away_team'] in game['player_stats']:
            for player in game['player_stats'][game['away_team']]:
                # Hitting stats
                if any(player.get(stat, 0) > 0 for stat in ['hits', 'runs', 'rbi', 'homeRuns', 'walks']):
                    away_hitting.append({
                        'Name': player['name'],
                        'H': player.get('hits', 0),
                        'R': player.get('runs', 0),
                        'RBI': player.get('rbi', 0),
                        'HR': player.get('homeRuns', 0),
                        'BB': player.get('walks', 0),
                        'K': player.get('strikeouts', 0)
                    })
                
                # Pitching stats
                if any(player.get(stat, 0) > 0 for stat in ['strikeouts', 'walks', 'hits_allowed', 'earned_runs', 'innings_pitched']):
                    away_pitching.append({
                        'Name': player['name'],
                        'IP': player.get('innings_pitched', '0.0'),
                        'H': player.get('hits_allowed', 0),
                        'R': player.get('earned_runs', 0),
                        'ER': player.get('earned_runs', 0),
                        'BB': player.get('walks', 0),
                        'K': player.get('strikeouts', 0)
                    })

        # Create DataFrames
        home_hitting_df = pd.DataFrame(home_hitting)
        home_pitching_df = pd.DataFrame(home_pitching)
        away_hitting_df = pd.DataFrame(away_hitting)
        away_pitching_df = pd.DataFrame(away_pitching)

        # Add team totals for hitting
        if not home_hitting_df.empty:
            home_hitting_totals = {
                'Name': 'TEAM TOTALS',
                'H': home_hitting_df['H'].sum(),
                'R': home_hitting_df['R'].sum(),
                'RBI': home_hitting_df['RBI'].sum(),
                'HR': home_hitting_df['HR'].sum(),
                'BB': home_hitting_df['BB'].sum(),
                'K': home_hitting_df['K'].sum()
            }
            home_hitting_df = pd.concat([home_hitting_df, pd.DataFrame([home_hitting_totals])], ignore_index=True)

        if not away_hitting_df.empty:
            away_hitting_totals = {
                'Name': 'TEAM TOTALS',
                'H': away_hitting_df['H'].sum(),
                'R': away_hitting_df['R'].sum(),
                'RBI': away_hitting_df['RBI'].sum(),
                'HR': away_hitting_df['HR'].sum(),
                'BB': away_hitting_df['BB'].sum(),
                'K': away_hitting_df['K'].sum()
            }
            away_hitting_df = pd.concat([away_hitting_df, pd.DataFrame([away_hitting_totals])], ignore_index=True)

        return home_hitting_df, home_pitching_df, away_hitting_df, away_pitching_df
    except Exception as e:
        print(f"Error creating box score: {str(e)}")
        return None, None, None, None

def calculate_team_stats(game):
    """
    Calculate and format team statistics from the game data
    Returns two dataframes: home_stats and away_stats
    """
    try:
        # Check if we have team stats data
        if 'team_stats' not in game or not game['team_stats']:
            return None, None
        
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Initialize dictionaries for team stats
        home_stats_dict = {}
        away_stats_dict = {}
        
        # Extract stats from game data
        for key, value in game['team_stats'].items():
            if key.startswith(f"{home_team}_"):
                stat_name = key.replace(f"{home_team}_", "")
                home_stats_dict[stat_name] = value
            elif key.startswith(f"{away_team}_"):
                stat_name = key.replace(f"{away_team}_", "")
                away_stats_dict[stat_name] = value
        
        # Process stats into dataframes
        if home_stats_dict:
            # Find hitting and pitching stats if they exist
            hitting_stats = None
            pitching_stats = None
            
            for key in home_stats_dict:
                if isinstance(home_stats_dict[key], dict) and 'stats' in home_stats_dict[key]:
                    for group in home_stats_dict[key]['stats']:
                        if group['type']['displayName'] == 'hitting':
                            hitting_stats = group['splits'][0]['stat'] if group['splits'] else None
                        elif group['type']['displayName'] == 'pitching':
                            pitching_stats = group['splits'][0]['stat'] if group['splits'] else None
            
            # Create dataframe for home team
            home_data = []
            
            if hitting_stats:
                home_data.append({"Category": "Batting Average", "Value": hitting_stats.get('avg', '0')})
                home_data.append({"Category": "OPS", "Value": hitting_stats.get('ops', '0')})
                home_data.append({"Category": "Runs", "Value": hitting_stats.get('runs', '0')})
                home_data.append({"Category": "Home Runs", "Value": hitting_stats.get('homeRuns', '0')})
                home_data.append({"Category": "RBI", "Value": hitting_stats.get('rbi', '0')})
            
            if pitching_stats:
                home_data.append({"Category": "ERA", "Value": pitching_stats.get('era', '0')})
                home_data.append({"Category": "WHIP", "Value": pitching_stats.get('whip', '0')})
                home_data.append({"Category": "Strikeouts", "Value": pitching_stats.get('strikeOuts', '0')})
                home_data.append({"Category": "Saves", "Value": pitching_stats.get('saves', '0')})
            
            home_stats_df = pd.DataFrame(home_data)
        else:
            home_stats_df = None
        
        if away_stats_dict:
            # Find hitting and pitching stats if they exist
            hitting_stats = None
            pitching_stats = None
            
            for key in away_stats_dict:
                if isinstance(away_stats_dict[key], dict) and 'stats' in away_stats_dict[key]:
                    for group in away_stats_dict[key]['stats']:
                        if group['type']['displayName'] == 'hitting':
                            hitting_stats = group['splits'][0]['stat'] if group['splits'] else None
                        elif group['type']['displayName'] == 'pitching':
                            pitching_stats = group['splits'][0]['stat'] if group['splits'] else None
            
            # Create dataframe for away team
            away_data = []
            
            if hitting_stats:
                away_data.append({"Category": "Batting Average", "Value": hitting_stats.get('avg', '0')})
                away_data.append({"Category": "OPS", "Value": hitting_stats.get('ops', '0')})
                away_data.append({"Category": "Runs", "Value": hitting_stats.get('runs', '0')})
                away_data.append({"Category": "Home Runs", "Value": hitting_stats.get('homeRuns', '0')})
                away_data.append({"Category": "RBI", "Value": hitting_stats.get('rbi', '0')})
            
            if pitching_stats:
                away_data.append({"Category": "ERA", "Value": pitching_stats.get('era', '0')})
                away_data.append({"Category": "WHIP", "Value": pitching_stats.get('whip', '0')})
                away_data.append({"Category": "Strikeouts", "Value": pitching_stats.get('strikeOuts', '0')})
                away_data.append({"Category": "Saves", "Value": pitching_stats.get('saves', '0')})
            
            away_stats_df = pd.DataFrame(away_data)
        else:
            away_stats_df = None
        
        return home_stats_df, away_stats_df
    except Exception as e:
        print(f"Error calculating team stats: {str(e)}")
        return None, None