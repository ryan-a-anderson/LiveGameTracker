import random
from datetime import datetime, timedelta
from nba_api.live.nba.endpoints import scoreboard
import json

def get_nba_live_games():
    """
    Fetch live NBA games using the NBA API
    """
    try:
        # Get today's games
        games_data = scoreboard.ScoreBoard()
        games_json = json.loads(games_data.get_json())
        nba_games = []

        for game in games_json['scoreboard']['games']:
            nba_games.append({
                "id": game['gameId'],
                "league": "NBA",
                "home_team": f"{game['homeTeam']['teamCity']} {game['homeTeam']['teamName']}",
                "away_team": f"{game['awayTeam']['teamCity']} {game['awayTeam']['teamName']}",
                "home_score": game['homeTeam']['score'],
                "away_score": game['awayTeam']['score'],
                "time": game['gameStatusText'],
                "status": "Live" if game['gameStatus'] == 2 else 
                         "Finished" if game['gameStatus'] == 3 else "Upcoming",
                "period": game.get('period', 0),
                "game_clock": game.get('gameClock', ''),
                "highlights": []  # We'll keep this empty for now as we don't have real highlights
            })

        return nba_games
    except Exception as e:
        print(f"Error fetching NBA games: {str(e)}")
        return []

def get_mock_games(leagues):
    """
    Generate mock games data for non-NBA leagues
    """
    games = []

    # Mock data for demonstration
    teams = {
        "NFL": [
            ("Kansas City Chiefs", "Las Vegas Raiders"),
            ("Buffalo Bills", "Miami Dolphins"),
            ("Green Bay Packers", "Chicago Bears")
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

    # Mock highlight videos
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
    for league in leagues:
        if league == "NBA":
            continue  # Skip NBA as we'll get real data

        for home, away in teams.get(league, []):
            # Generate random scores
            home_score = random.randint(0, 5)
            away_score = random.randint(0, 5)

            # Generate random game time
            current_time = datetime.now()
            game_time = current_time - timedelta(minutes=random.randint(0, 90))

            status = random.choice(["Live", "Upcoming", "Finished"])

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

def get_live_games(selected_leagues, status_filter):
    """
    Combine real NBA data with mock data for other sports
    """
    games = []

    # Get real NBA data if NBA is selected
    if "NBA" in selected_leagues:
        nba_games = get_nba_live_games()
        if status_filter != "All":
            nba_games = [g for g in nba_games if g['status'] == status_filter]
        games.extend(nba_games)

    # Get mock data for other sports
    mock_games = get_mock_games(selected_leagues)
    if status_filter != "All":
        mock_games = [g for g in mock_games if g['status'] == status_filter]
    games.extend(mock_games)

    # Sort games by time
    games.sort(key=lambda x: x['time'])

    return games