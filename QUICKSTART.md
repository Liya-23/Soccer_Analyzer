# Soccer Match Analyzer - Quick Start

## Installation & Run

```bash
cd soccer_analyzer

# Option 1: Use the startup script (Linux/Mac)
chmod +x run.sh
./run.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python app.py
```

Server starts at: **http://localhost:8888**

## Usage

### Web Interface
1. Go to http://localhost:8888
2. Select home and away teams
3. Click "Analyze Match"
4. Review the analysis with verification badges (🟢/🟡/🔴)

### API
```bash
curl "http://localhost:8888/api/match?home=Liverpool&away=Arsenal"
```

Returns comprehensive JSON analysis.

## Key Features

- **Probability Model**: xG-based with form, rest, injuries, H2H weighting
- **Value Detection**: Compares model odds vs bookmaker odds
- **Transparent Data**: Every data point marked as verified/assumed/missing
- **Pluggable Data Layer**: Easy to swap mock provider for real data sources
- **Cached**: SQLite caching prevents repeated API calls

## Understanding the Analysis

### Odds Table
- **Model**: What the probability model calculated
- **Fair Odds**: Implied odds from model probability (1/probability)
- **Book**: Actual bookmaker odds
- **Edge**: Positive % = model sees value, negative % = bookmaker favored

### Confidence Score
- Based on data completeness + xG convergence
- 70%+ = Medium-high confidence
- 50-70% = Medium
- <50% = Low (incomplete/conflicting data)

### Verification States
- 🟢 **Verified**: Retrieved from trusted source
- 🟡 **Assumption**: Statistical inference
- 🔴 **Unavailable**: Couldn't be verified

## Customization

### Adjust model weights
Edit `models/probability.py`:
```python
class ModelWeights:
    xg_weight: float = 0.40      # 40% importance to xG
    form_weight: float = 0.25     # 25% to form
    rest_weight: float = 0.15     # etc.
    injuries_weight: float = 0.10
    h2h_weight: float = 0.10
```

### Change bet threshold
Edit `handlers/analyze.py`:
```python
recommendation = "BET" if best_edge >= 3.0 else "MARGINAL" if best_edge >= 1.0 else "NO BET"
```

### Add real data source
Create a class in `services/data_provider.py` inheriting from `FootballDataProvider`.

## Project Structure

```
soccer_analyzer/
├── app.py                    # Main Tornado app
├── requirements.txt          # Dependencies
├── run.sh                    # Startup script
├── handlers/
│   ├── home.py              # / route
│   ├── analyze.py           # /analyze route
│   └── api.py               # /api/match route
├── services/
│   └── data_provider.py     # Data abstraction layer
├── models/
│   └── probability.py       # Poisson + weighting model
├── templates/
│   ├── index.html           # Input page
│   └── analysis.html        # Results page
└── static/
    ├── css/style.css        # Dark theme sports UI
    └── js/app.js            # Frontend JS
```

## Troubleshooting

**Port 8888 already in use?**
```bash
python app.py --port=9999
```

**Module import errors?**
Ensure you're in the virtual environment:
```bash
source venv/bin/activate
```

**Cache not clearing?**
Delete `cache.db` and restart server.

## Next Steps

1. **Add real data**: Integrate Understat, StatsBomb, Opta APIs
2. **LLM layer**: Add Claude API for narrative analysis
3. **Backtesting**: Validate model edge against historical results
4. **Live updates**: Real-time odds from multiple sportsbooks
5. **User accounts**: Save analysis history
