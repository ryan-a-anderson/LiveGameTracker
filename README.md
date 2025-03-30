# Live Game Tracker

A real-time sports game tracking application that provides live scores, statistics, and game summaries for MLB games.

## Features

- Live game scores and status
- Detailed game summaries with player statistics
- Advanced statistics visualization
- Box scores for completed games
- Game highlights
- Intelligent caching for optimal performance

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LiveGameTracker.git
cd LiveGameTracker
```

2. Create and activate a conda environment:
```bash
conda create -n livegame python=3.11
conda activate livegame
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
MLB_API_KEY=your_mlb_api_key
GEMINI_API_KEY=your_gemini_api_key
REDIS_URL=your_redis_url  # Optional, for production
```

5. Run the application:
```bash
streamlit run main.py
```

## Environment Variables

- `MLB_API_KEY`: Your MLB Stats API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `REDIS_URL`: (Optional) Redis URL for production caching

## Development

The application uses:
- Streamlit for the web interface
- MLB Stats API for game data
- Google Gemini API for game summaries
- Redis for caching (optional)
- Plotly for visualizations

## License

MIT License 