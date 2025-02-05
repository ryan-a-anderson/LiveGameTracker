import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

def generate_team_stats(game):
    """
    Generate mock advanced statistics for teams
    """
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

def create_possession_chart(stats, home_team, away_team):
    """
    Create a pie chart showing possession statistics
    """
    fig = px.pie(
        values=[stats['possession'][home_team], stats['possession'][away_team]],
        names=[home_team, away_team],
        title="Ball Possession (%)",
        color_discrete_sequence=["#2ecc71", "#e74c3c"]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_shots_comparison(stats, home_team, away_team):
    """
    Create a bar chart comparing shots and shots on target
    """
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

def create_score_timeline(game):
    """
    Create a line chart showing score progression
    """
    # Generate mock score timeline
    minutes = list(range(0, int((datetime.now() - 
        (datetime.strptime(game['time'], '%H:%M') - 
         timedelta(minutes=90))).total_seconds() / 60)))
    
    home_scores = [0]
    away_scores = [0]
    current_home = 0
    current_away = 0
    
    # Generate random scoring events
    for _ in range(game['home_score'] + game['away_score']):
        minute = random.choice(minutes)
        if random.random() < 0.5 and current_home < game['home_score']:
            current_home += 1
            home_scores.append((minute, current_home))
        elif current_away < game['away_score']:
            current_away += 1
            away_scores.append((minute, current_away))
    
    # Sort by minute
    home_scores.sort()
    away_scores.sort()
    
    # Create the line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[score[0] for score in home_scores],
        y=[score[1] for score in home_scores],
        name=game['home_team'],
        line=dict(color="#2ecc71", width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=[score[0] for score in away_scores],
        y=[score[1] for score in away_scores],
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

def create_pass_accuracy_gauge(team, accuracy):
    """
    Create a gauge chart showing pass accuracy
    """
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
