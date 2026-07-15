# SEC Survivor Basketball 2026

Retrospective time-machine site for the 2025-26 SEC basketball survivor pool.

## Files

- `index.html` - the GitHub Pages site
- `engine.js` - survivor logic used by the page
- `data/schedule.json` - weekly team schedules generated from the grid
- `data/picks.json` - player picks
- `data/results.json` - final scores; currently empty until imported
- `scripts/simulate.py` - command-line validation engine
- `scripts/import_results.py` - one-time Sports-Reference importer

## Local test

Because the page fetches local JSON files, serve the folder instead of opening `index.html` directly:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Add final scores

```bash
pip install pandas lxml requests
python scripts/import_results.py
python scripts/simulate.py
```
