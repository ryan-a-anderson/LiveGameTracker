import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

def generate_team_stats(game):
    """
    Generate mock advanced statistics for teams
    """
    try:
        stats = {
            'possession': {
                game['home_team']: random.randint(40, 60),
                game['away_team']: None  # Will be calculated as complement
            },
            'shots': {
                game['home_team']: random.randint(8, 20),
                game['away_team']: random.randint(8, 20)
            },
            'shots_on_target': {
                game['home_team']: random.randint(3, 10),
                game['away_team']: random.randint(3, 10)
            },
            'pass_accuracy': {
                game['home_team']: random.randint(70, 90),
                game['away_team']: random.randint(70, 90)
            }
        }

        # Calculate complement for possession
        stats['possession'][game['away_team']] = 100 - stats['possession'][game['home_team']]

        return stats
    except Exception as e:
        print(f"Error generating team stats: {str(e)}")
        return None

def create_possession_chart(stats, home_team, away_team):
    """
    Create a pie chart showing possession statistics
    """
    try:
        fig = px.pie(
            values=[stats['possession'][home_team], stats['possession'][away_team]],
            names=[home_team, away_team],
            title="Ball Possession (%)",
            color_discrete_sequence=["#2ecc71", "#e74c3c"]
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    except Exception as e:
        print(f"Error creating possession chart: {str(e)}")
        return None

def create_shots_comparison(stats, home_team, away_team):
    """
    Create a bar chart comparing shots and shots on target
    """
    try:
        categories = ['Total Shots', 'Shots on Target']

        fig = go.Figure(data=[
            go.Bar(name=home_team, 
                   x=categories,
                   y=[stats['shots'][home_team], 
                      stats['shots_on_target'][home_team]],
                   marker_color='#2ecc71'),
            go.Bar(name=away_team, 
                   x=categories,
                   y=[stats['shots'][away_team], 
                      stats['shots_on_target'][away_team]],
                   marker_color='#e74c3c')
        ])

        fig.update_layout(
            title="Shot Analysis",
            barmode='group',
            xaxis_title="Metric",
            yaxis_title="Count"
        )
        return fig
    except Exception as e:
        print(f"Error creating shots comparison: {str(e)}")
        return None

def create_score_timeline(game):
    """
    Create a line chart showing score progression
    """
    try:
        # Calculate time range for the game
        current_time = datetime.now()
        try:
            game_time = datetime.strptime(game['time'], '%H:%M')
            game_time = game_time.replace(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day
            )
        except ValueError:
            # Fallback to current time if parsing fails
            game_time = current_time - timedelta(minutes=90)

        minutes = list(range(90))  # Fixed 90-minute range for consistency

        # Initialize timeline data
        timeline_data = {
            'minute': [0],
            f"{game['home_team']}_score": [0],
            f"{game['away_team']}_score": [0]
        }

        current_home = 0
        current_away = 0

        # Generate random scoring events
        for _ in range(game['home_score'] + game['away_score']):
            minute = random.choice(minutes[1:])  # Exclude minute 0
            if random.random() < 0.5 and current_home < game['home_score']:
                current_home += 1
                timeline_data['minute'].append(minute)
                timeline_data[f"{game['home_team']}_score"].append(current_home)
                timeline_data[f"{game['away_team']}_score"].append(current_away)
            elif current_away < game['away_score']:
                current_away += 1
                timeline_data['minute'].append(minute)
                timeline_data[f"{game['home_team']}_score"].append(current_home)
                timeline_data[f"{game['away_team']}_score"].append(current_away)

        # Ensure final scores match
        if timeline_data[f"{game['home_team']}_score"][-1] != game['home_score']:
            timeline_data['minute'].append(89)
            timeline_data[f"{game['home_team']}_score"].append(game['home_score'])
            timeline_data[f"{game['away_team']}_score"].append(current_away)

        if timeline_data[f"{game['away_team']}_score"][-1] != game['away_score']:
            timeline_data['minute'].append(89)
            timeline_data[f"{game['home_team']}_score"].append(game['home_score'])
            timeline_data[f"{game['away_team']}_score"].append(game['away_score'])

        # Convert to DataFrame and sort by minute
        df = pd.DataFrame(timeline_data).sort_values('minute')

        # Create the line chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['minute'],
            y=df[f"{game['home_team']}_score"],
            name=game['home_team'],
            line=dict(color="#2ecc71", width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df['minute'],
            y=df[f"{game['away_team']}_score"],
            name=game['away_team'],
            line=dict(color="#e74c3c", width=2)
        ))

        fig.update_layout(
            title="Score Progression",
            xaxis_title="Match Time (minutes)",
            yaxis_title="Goals",
            hovermode="x unified"
        )

        return fig
    except Exception as e:
        print(f"Error creating score timeline: {str(e)}")
        return None

def create_pass_accuracy_gauge(team, accuracy):
    """
    Create a gauge chart showing pass accuracy
    """
    try:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = accuracy,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{team} Pass Accuracy"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 60], 'color': "#ff5733"},
                    {'range': [60, 75], 'color': "#ffa33f"},
                    {'range': [75, 100], 'color': "#33ff57"}
                ]
            }
        ))

        return fig
    except Exception as e:
        print(f"Error creating pass accuracy gauge: {str(e)}")
        return None