import json
import random

def generate_game_summary(game):
    """
    Generate a mock summary of the current game state
    """
    # Mock summary templates
    summaries = [
        {
            "summary": f"Exciting match between {game['home_team']} and {game['away_team']}! Current score {game['home_score']}-{game['away_score']}.",
            "highlights": ["Great defensive play", "Fast-paced action", "Crowd is energetic"],
            "key_players": [
                {"name": "Player 1", "performance": "Outstanding"},
                {"name": "Player 2", "performance": "Solid defense"}
            ]
        },
        {
            "summary": f"Intense battle at the {game['league']} game! {game['home_team']} vs {game['away_team']} at {game['time']}.",
            "highlights": ["Multiple scoring opportunities", "Strong teamwork", "High energy"],
            "key_players": [
                {"name": "Player A", "performance": "Scored twice"},
                {"name": "Player B", "performance": "Great assists"}
            ]
        }
    ]

    return json.dumps(random.choice(summaries), indent=2)