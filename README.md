# 🏈 FF Draft Vote

Fantasy football destination voting app — 2 rounds, live leaderboard, browser memory.

## Quick setup before you deploy

1. **Open `app.py`** and change the two lines at the top:
   ```python
   DRAFT_YEAR = 2025          # ← your year
   CITIES = [                 # ← your 4 candidate cities
       "Las Vegas, NV 🎰",
       "Nashville, TN 🎸",
       "New Orleans, LA 🎺",
       "Austin, TX 🤠",
   ]
   ```

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a **GitHub repo** (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) → "New app".
3. Pick your repo + branch, set **Main file path** to `app.py`.
4. Click **Deploy** — you'll get a sharable URL in ~1 minute.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How it works

| Step | What happens |
|------|-------------|
| Page load | Browser checks localStorage — if your name is saved, you're auto-identified |
| Round 1 | Each person picks exactly 2 of the 4 cities |
| Leaderboard | Live vote counts + who voted for each city, auto-refreshes every 20 s |
| Admin: End Round 1 | Locks votes, picks top 2 cities, advances to Championship |
| Round 2 | Each person gets ONE vote between the 2 finalists |
| Admin: Declare Winner | Reveals the destination with balloons 🎈 |

## Admin controls

Both "End of Round 1" and "Declare the Winner" buttons are hidden inside
**expanders at the bottom** of the page so nobody clicks them accidentally.
There's also a "Reset All Votes" expander if you need to start over during testing.
