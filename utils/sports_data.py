import random
from datetime import datetime, timedelta
from nba_api.live.nba.endpoints import scoreboard
import json
import os
import requests
from typing import List, Dict, Any, Optional
from functools import lru_cache
import redis
import time

# API Keys and endpoints
FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
MLB_API_KEY = os.getenv('MLB_API_KEY')
NFL_API_KEY = os.getenv('NFL_API_KEY')

# Initialize Redis connection (if REDIS_URL is set in environment)
redis_client = None
if 'REDIS_URL' in os.environ:
    try:
        redis_client = redis.from_url(os.environ['REDIS_URL'])
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

# Cache configuration
CACHE_TTL = {
    'live_games': 60,  # 1 minute for live games
    'upcoming_games': 300,  # 5 minutes for upcoming games
    'finished_games': 3600,  # 1 hour for finished games
    'team_stats': 86400,  # 24 hours for team stats
    'player_stats': 3600,  # 1 hour for player stats
}

# Rate limiting configuration
RATE_LIMIT = {
    'requests_per_minute': 30,
    'min_interval': 2  # minimum seconds between requests
}

_last_request_time = 0

def _rate_limit():
    """Implement rate limiting"""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    if time_since_last < RATE_LIMIT['min_interval']:
        time.sleep(RATE_LIMIT['min_interval'] - time_since_last)
    _last_request_time = time.time()

def _get_cached_data(key: str) -> Optional[Dict]:
    """Get data from Redis cache"""
    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Redis cache error: {e}")
    return None

def _set_cached_data(key: str, data: Dict, ttl: int):
    """Set data in Redis cache with TTL"""
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"Redis cache error: {e}")

def _is_cache_valid(cache_time: datetime) -> bool:
    """Check if the cache is still valid"""
    if cache_time is None:
        return False
    return (datetime.now() - cache_time).total_seconds() < CACHE_DURATION

def _get_mlb_teams() -> Dict[str, int]:
    """Get MLB teams with caching"""
    global _mlb_teams_cache, _mlb_teams_cache_time
    
    if _is_cache_valid(_mlb_teams_cache_time):
        return _mlb_teams_cache
    
    try:
        teams_response = requests.get(
            'https://statsapi.mlb.com/api/v1/teams',
            params={
                'sportId': 1,  # MLB
                'fields': 'teams,id,name,abbreviation'
            }
        )
        teams_response.raise_for_status()
        teams_data = teams_response.json()
        
        # Create a mapping of team names to IDs
        team_id_map = {}
        for team in teams_data['teams']:
            team_id_map[team['name']] = team['id']
        
        _mlb_teams_cache = team_id_map
        _mlb_teams_cache_time = datetime.now()
        return team_id_map
    except Exception as e:
        print(f"Error fetching MLB teams: {str(e)}")
        return {}

def _get_team_stats(team_id: int) -> Dict[str, Any]:
    """Get team stats with caching"""
    if team_id in _team_stats_cache:
        cache_data = _team_stats_cache[team_id]
        if _is_cache_valid(cache_data['timestamp']):
            return cache_data['data']
    
    try:
        stats = {}
        # Get both 2024 and 2025 season stats
        for season in ['2024', '2025']:
            stats_response = requests.get(
                'https://statsapi.mlb.com/api/v1/teams',
                params={
                    'teamIds': team_id,
                    'hydrate': 'stats(group=hitting,pitching,regularSeason)',
                    'season': season
                }
            )
            stats_response.raise_for_status()
            stats_data = stats_response.json()
            
            if 'teams' in stats_data and len(stats_data['teams']) > 0:
                team = stats_data['teams'][0]
                if 'stats' in team:
                    for stat_group in team['stats']:
                        if stat_group['group'] == 'hitting':
                            stats[f'{season}_hitting'] = {
                                'runs': stat_group['stats'].get('runs', 0),
                                'hits': stat_group['stats'].get('hits', 0),
                                'homeRuns': stat_group['stats'].get('homeRuns', 0),
                                'battingAvg': stat_group['stats'].get('avg', '0.000')
                            }
                        elif stat_group['group'] == 'pitching':
                            stats[f'{season}_pitching'] = {
                                'era': stat_group['stats'].get('era', '0.00'),
                                'wins': stat_group['stats'].get('wins', 0),
                                'losses': stat_group['stats'].get('losses', 0),
                                'strikeouts': stat_group['stats'].get('strikeOuts', 0)
                            }
        
        _team_stats_cache[team_id] = {
            'data': stats,
            'timestamp': datetime.now()
        }
        return stats
    except Exception as e:
        print(f"Error fetching team stats for team {team_id}: {str(e)}")
    return {}

def get_nba_live_games() -> List[Dict[str, Any]]:
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

def get_premier_league_games() -> List[Dict[str, Any]]:
    """
    Fetch Premier League games using the Football-Data.org API
    """
    try:
        headers = {'X-Auth-Token': FOOTBALL_DATA_API_KEY}
        response = requests.get(
            'http://api.football-data.org/v4/competitions/PL/matches',
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        games = []
        for match in data['matches']:
            games.append({
                "id": match['id'],
                "league": "Premier League",
                "home_team": match['homeTeam']['name'],
                "away_team": match['awayTeam']['name'],
                "home_score": match['score']['fullTime']['home'] if match['score']['fullTime']['home'] is not None else 0,
                "away_score": match['score']['fullTime']['away'] if match['score']['fullTime']['away'] is not None else 0,
                "time": match['utcDate'],
                "status": "Live" if match['status'] == "IN_PROGRESS" else
                         "Finished" if match['status'] == "FINISHED" else "Upcoming",
                "period": match.get('minute', None),
                "game_clock": f"{match.get('minute', 0)}'",
                "highlights": []
            })
        return games
    except Exception as e:
        print(f"Error fetching Premier League games: {str(e)}")
        return []

def get_mlb_games(selected_date=None) -> List[Dict[str, Any]]:
    """
    Fetch MLB games using the MLB Stats API with caching
    
    Args:
        selected_date: Optional date to fetch games for (datetime object).
                      If None, uses today's date.
    """
    global _mlb_schedule_cache, _mlb_schedule_cache_time
    
    try:
        # Use selected date or today's date
        date_str = selected_date.strftime('%Y-%m-%d') if selected_date else datetime.now().strftime('%Y-%m-%d')
        
        # Check if we have cached data for this date
        if date_str in _mlb_schedule_cache and _is_cache_valid(_mlb_schedule_cache_time):
            return _mlb_schedule_cache[date_str]
        
        # Get team IDs from cache
        team_id_map = _get_mlb_teams()
        
        # Get the schedule
        response = requests.get(
            'https://statsapi.mlb.com/api/v1/schedule',
            params={
                'sportId': 1,  # MLB
                'date': date_str,
                'fields': 'dates,games,gamePk,teams,home,away,team,name,score,status,detailedState,currentInning,gameDate,linescore,decisions'
            }
        )
        response.raise_for_status()
        data = response.json()
        
        games = []
        if 'dates' in data and len(data['dates']) > 0:
            for game in data['dates'][0]['games']:
                try:
                    # Get team names
                    home_team = game['teams']['home']['team']['name']
                    away_team = game['teams']['away']['team']['name']
                    
                    # Get team IDs from our mapping
                    home_team_id = team_id_map.get(home_team)
                    away_team_id = team_id_map.get(away_team)
                    
                    if not home_team_id or not away_team_id:
                        print(f"Could not find team IDs for {home_team} vs {away_team}")
                        continue
                    
                    # Get scores
                    home_score = game['teams']['home'].get('score', 0)
                    away_score = game['teams']['away'].get('score', 0)
                    
                    # Get game status
                    detailed_state = game['status'].get('detailedState', '')
                    
                    # Get game time 
                    game_time = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ')
                    
                    # Determine game status based on detailed state and date
                    if detailed_state == "Final":
                        status = "Finished"
                    elif detailed_state == "In Progress":
                        status = "Live"
                    elif detailed_state == "Delayed":
                        status = "Delayed"
                    elif detailed_state == "Postponed":
                        status = "Postponed"
                    elif detailed_state == "Scheduled":
                        status = "Upcoming"
                    else:
                        # For past dates, consider all games as finished
                        if selected_date and selected_date < datetime.now().date():
                            status = "Finished"
                        # If we have a score and the game time has passed, it's likely finished
                        elif game_time < datetime.now() and (home_score > 0 or away_score > 0):
                            status = "Finished"
                        else:
                            status = "Upcoming"
                    
                    # Format the time
                    formatted_time = game_time.strftime('%H:%M')
                    
                    # Get inning information
                    inning = game.get('currentInning', None)
                    inning_state = game.get('detailedState', '')
                    
                    # Initialize player_stats and highlights variables
                    player_stats = {}
                    highlights = []
                    
                    # Get player statistics for completed games
                    if status == "Finished":
                        try:
                            # Get live feed data for player stats
                            live_feed_response = requests.get(
                                f'https://statsapi.mlb.com/api/v1.1/game/{game["gamePk"]}/feed/live'
                            )
                            live_feed_response.raise_for_status()
                            live_feed_data = live_feed_response.json()
                            
                            # Process home team stats
                            if 'home' in live_feed_data.get('liveData', {}).get('boxscore', {}).get('teams', {}):
                                home_stats = []
                                for player in live_feed_data['liveData']['boxscore']['teams']['home']['players'].values():
                                    player_data = {'name': player['person']['fullName']}
                                    
                                    # Get batting stats
                                    if 'stats' in player and 'batting' in player['stats']:
                                        batting_stats = player['stats']['batting']
                                        if any(batting_stats.get(stat, 0) > 0 for stat in ['hits', 'runs', 'rbi', 'homeRuns']):
                                            player_data.update({
                                                'hits': batting_stats.get('hits', 0),
                                                'runs': batting_stats.get('runs', 0),
                                                'rbi': batting_stats.get('rbi', 0),
                                                'homeRuns': batting_stats.get('homeRuns', 0)
                                            })
                                    
                                    # Get pitching stats
                                    if 'stats' in player and 'pitching' in player['stats']:
                                        pitching_stats = player['stats']['pitching']
                                        if any(pitching_stats.get(stat, 0) > 0 for stat in ['strikeOuts', 'hits', 'runs', 'earnedRuns', 'walks']):
                                            player_data.update({
                                                'strikeouts': pitching_stats.get('strikeOuts', 0),
                                                'hits_allowed': pitching_stats.get('hits', 0),
                                                'runs_allowed': pitching_stats.get('runs', 0),
                                                'earned_runs': pitching_stats.get('earnedRuns', 0),
                                                'walks': pitching_stats.get('walks', 0),
                                                'innings_pitched': pitching_stats.get('inningsPitched', '0.0')
                                            })
                                    
                                    if len(player_data) > 1:  # Only add if we have stats
                                        home_stats.append(player_data)
                                player_stats[home_team] = home_stats
                            
                            # Process away team stats
                            if 'away' in live_feed_data.get('liveData', {}).get('boxscore', {}).get('teams', {}):
                                away_stats = []
                                for player in live_feed_data['liveData']['boxscore']['teams']['away']['players'].values():
                                    player_data = {'name': player['person']['fullName']}
                                    
                                    # Get batting stats
                                    if 'stats' in player and 'batting' in player['stats']:
                                        batting_stats = player['stats']['batting']
                                        if any(batting_stats.get(stat, 0) > 0 for stat in ['hits', 'runs', 'rbi', 'homeRuns']):
                                            player_data.update({
                                                'hits': batting_stats.get('hits', 0),
                                                'runs': batting_stats.get('runs', 0),
                                                'rbi': batting_stats.get('rbi', 0),
                                                'homeRuns': batting_stats.get('homeRuns', 0)
                                            })
                                    
                                    # Get pitching stats
                                    if 'stats' in player and 'pitching' in player['stats']:
                                        pitching_stats = player['stats']['pitching']
                                        if any(pitching_stats.get(stat, 0) > 0 for stat in ['strikeOuts', 'hits', 'runs', 'earnedRuns', 'walks']):
                                            player_data.update({
                                                'strikeouts': pitching_stats.get('strikeOuts', 0),
                                                'hits_allowed': pitching_stats.get('hits', 0),
                                                'runs_allowed': pitching_stats.get('runs', 0),
                                                'earned_runs': pitching_stats.get('earnedRuns', 0),
                                                'walks': pitching_stats.get('walks', 0),
                                                'innings_pitched': pitching_stats.get('inningsPitched', '0.0')
                                            })
                                    
                                    if len(player_data) > 1:  # Only add if we have stats
                                        away_stats.append(player_data)
                                player_stats[away_team] = away_stats
                            
                            # Get highlights
                            if 'highlights' in live_feed_data.get('liveData', {}):
                                for highlight in live_feed_data['liveData']['highlights'].get('highlights', []):
                                    highlights.append({
                                        'description': highlight.get('headline', ''),
                                        'timestamp': highlight.get('timestamp', '')
                                    })
                        except Exception as e:
                            print(f"Error fetching player stats for game {game['gamePk']}: {str(e)}")
                            player_stats = {}
                            highlights = []
                    
                    # Get winning and losing pitchers
                    decisions = game.get('decisions', {})
                    winning_pitcher = decisions.get('winner', {})
                    losing_pitcher = decisions.get('loser', {})
                    
                    # Get save pitcher if available
                    save_pitcher = decisions.get('save', {})
                    
                    # Get team season stats for all games
                    team_stats = {}
                    # Get cached stats for both teams
                    home_stats = _get_team_stats(home_team_id)
                    away_stats = _get_team_stats(away_team_id)
                    
                    # Add home team stats with proper formatting
                    if home_stats:
                        for key, value in home_stats.items():
                            team_stats[f"{home_team}_{key}"] = value
                    
                    # Add away team stats with proper formatting
                    if away_stats:
                        for key, value in away_stats.items():
                            team_stats[f"{away_team}_{key}"] = value
                    
                    # Get linescore data
                    linescore = game.get('linescore', {})
                    
                    # Print debug information
                    print(f"\nFound game: {home_team} vs {away_team}")
                    print(f"Status: {status} (State: {detailed_state})")
                    print(f"Score: {home_score} - {away_score}")
                    print(f"Time: {formatted_time}")
                    print(f"Date: {date_str}")
                    print(f"Inning: {inning}")
                    print(f"State: {inning_state}")
                    print("---")
                    
                    games.append({
                        "id": game['gamePk'],
                        "league": "MLB",
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": home_score,
                        "away_score": away_score,
                        "time": formatted_time,
                        "date": date_str,
                        "status": status,
                        "period": inning,
                        "game_clock": inning_state,
                        "highlights": highlights,
                        "player_stats": player_stats,
                        "winning_pitcher": winning_pitcher.get('fullName', ''),
                        "losing_pitcher": losing_pitcher.get('fullName', ''),
                        "save_pitcher": save_pitcher.get('fullName', ''),
                        "team_stats": team_stats,
                        "linescore": linescore
                    })
                except Exception as e:
                    print(f"Error processing game: {str(e)}")
                    continue
        
        print(f"Total games found for {date_str}: {len(games)}")
        
        # Cache the games for this date
        _mlb_schedule_cache[date_str] = games
        _mlb_schedule_cache_time = datetime.now()
        
        # Clean up old cache entries (keep only yesterday, today, and tomorrow)
        today = datetime.now().date()
        cache_dates = list(_mlb_schedule_cache.keys())
        for cache_date in cache_dates:
            cache_date_obj = datetime.strptime(cache_date, '%Y-%m-%d').date()
            if abs((cache_date_obj - today).days) > 1:  # Keep only yesterday, today, and tomorrow
                del _mlb_schedule_cache[cache_date]
        
        return games
    except Exception as e:
        print(f"Error fetching MLB games: {str(e)}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
        return []

def get_nfl_games() -> List[Dict[str, Any]]:
    """
    Fetch NFL games using the NFL API
    """
    try:
        headers = {'Authorization': f'Bearer {NFL_API_KEY}'}
        response = requests.get(
            'https://api.nfl.com/v1/games',
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        games = []
        for game in data['games']:
            games.append({
                "id": game['id'],
                "league": "NFL",
                "home_team": game['homeTeam']['abbr'],
                "away_team": game['awayTeam']['abbr'],
                "home_score": game['homeTeam']['score'],
                "away_score": game['awayTeam']['score'],
                "time": game['gameTime'],
                "status": "Live" if game['gameStatus'] == "IN_PROGRESS" else
                         "Finished" if game['gameStatus'] == "FINAL" else "Upcoming",
                "period": game.get('quarter', None),
                "game_clock": game.get('gameClock', ''),
                "highlights": []
            })
        return games
    except Exception as e:
        print(f"Error fetching NFL games: {str(e)}")
        return []

def get_mock_games(leagues: List[str]) -> List[Dict[str, Any]]:
    """
    Generate mock games data for non-implemented leagues or when APIs fail
    """
    games = []

    # Mock data for demonstration
    teams = {
        "MLB": [
            ("New York Yankees", "Boston Red Sox"),
            ("Los Angeles Dodgers", "San Francisco Giants"),
            ("Chicago Cubs", "St. Louis Cardinals")
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
        if league != "MLB":  # Skip non-MLB leagues
            continue

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

def get_live_games(selected_leagues: List[str], status_filter: str, selected_date=None) -> List[Dict[str, Any]]:
    """
    Combine real MLB data with mock data if API fails
    
    Args:
        selected_leagues: List of leagues to get games for
        status_filter: Filter for game status (All, Live, Upcoming, Finished)
        selected_date: Optional date to fetch games for (datetime object).
                      If None, uses today's date.
    """
    games = []

    # Get real MLB data if MLB is selected
    if "MLB" in selected_leagues:
        mlb_games = get_mlb_games(selected_date)
        if status_filter != "All":
            mlb_games = [g for g in mlb_games if g['status'] == status_filter]
        games.extend(mlb_games)

    # If we got no games from real API, fall back to mock data
    if not games:
        mock_games = get_mock_games(selected_leagues)
        if status_filter != "All":
            mock_games = [g for g in mock_games if g['status'] == status_filter]
        games.extend(mock_games)

    # Sort games by time
    games.sort(key=lambda x: x['time'])

    return games

def pre_cache_games():
    """Pre-cache games for yesterday, today, and tomorrow with intelligent timing"""
    today = datetime.now().date()
    
    # Only cache yesterday's games if they're finished
    yesterday = today - timedelta(days=1)
    get_live_games(["MLB"], "Finished", yesterday)
    
    # Cache today's games based on time of day
    current_hour = datetime.now().hour
    if current_hour < 12:  # Morning
        get_live_games(["MLB"], "Upcoming", today)
    elif current_hour < 20:  # Afternoon/Evening
        get_live_games(["MLB"], "All", today)
    else:  # Night
        get_live_games(["MLB"], "Finished", today)
    
    # Cache tomorrow's games
    tomorrow = today + timedelta(days=1)
    get_live_games(["MLB"], "Upcoming", tomorrow)