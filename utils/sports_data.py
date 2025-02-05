import random
from datetime import datetime, timedelta

def get_live_games(selected_leagues, status_filter):
    """
    Mock function to generate live games data.
    In production, this would integrate with real sports APIs.
    """
    games = []

    # Mock data for demonstration
    teams = {
        "NFL": [
            ("Kansas City Chiefs", "Las Vegas Raiders"),
            ("Buffalo Bills", "Miami Dolphins"),
            ("Green Bay Packers", "Chicago Bears")
        ],
        "NBA": [
            ("Los Angeles Lakers", "Golden State Warriors"),
            ("Boston Celtics", "Brooklyn Nets"),
            ("Milwaukee Bucks", "Philadelphia 76ers")
        ],
        "MLB": [
            ("New York Yankees", "Boston Red Sox"),
            ("Los Angeles Dodgers", "San Francisco Giants"),
            ("Chicago Cubs", "St. Louis Cardinals")
        ],
        "Premier League": [
            ("Manchester City", "Liverpool"),
            ("Arsenal", "Chelsea"),
            ("Manchester United", "Tottenham")
        ]
    }

    # Mock highlight videos (in production, these would be real URLs)
    highlight_videos = [
        {
            "title": "Amazing Play",
            "timestamp": "12:34",
            "thumbnail": "https://example.com/thumbnail1.jpg",
            "description": "Incredible defensive save!"
        },
        {
            "title": "Game-changing Moment",
            "timestamp": "23:45",
            "thumbnail": "https://example.com/thumbnail2.jpg",
            "description": "Amazing scoring opportunity!"
        }
    ]

    game_id = 1
    for league in selected_leagues:
        for home, away in teams[league]:
            # Generate random scores
            home_score = random.randint(0, 5)
            away_score = random.randint(0, 5)

            # Generate random game time
            current_time = datetime.now()
            game_time = current_time - timedelta(minutes=random.randint(0, 90))

            status = random.choice(["Live", "Upcoming", "Finished"])
            if status_filter != "All" and status != status_filter:
                continue

            games.append({
                "id": game_id,
                "league": league,
                "home_team": home,
                "away_team": away,
                "home_score": home_score,
                "away_score": away_score,
                "time": game_time.strftime("%H:%M"),
                "status": status,
                "highlights": random.sample(highlight_videos, random.randint(1, 2))
            })
            game_id += 1

    return games