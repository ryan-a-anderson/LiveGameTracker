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

    selected = random.choice(summaries)

    # Format the summary in a readable way
    formatted_summary = f"""
📊 Game Summary
---------------
{selected['summary']}

🎯 Key Highlights:
{chr(8226)} {selected['highlights'][0]}
{chr(8226)} {selected['highlights'][1]}
{chr(8226)} {selected['highlights'][2]}

⭐ Notable Players:
{chr(8226)} {selected['key_players'][0]['name']}: {selected['key_players'][0]['performance']}
{chr(8226)} {selected['key_players'][1]['name']}: {selected['key_players'][1]['performance']}
"""

    return formatted_summary