import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_STRIKES = 3

def norm(value):
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in str(value or "")).split())

def same(a, b):
    return norm(a) == norm(b)

def load(name):
    return json.loads((ROOT / "data" / name).read_text())

def get_pick(picks, player, week):
    return next((p for p in picks if same(p.get("player"), player) and int(p.get("week")) == week), None)

def get_team_week(schedule, team, week):
    return next((s for s in schedule if same(s.get("team"), team) and int(s.get("week")) == week), None)

def find_result(results, date, team, opponent):
    for r in results:
        if r.get("date") != date:
            continue
        has_team = same(r.get("home"), team) or same(r.get("away"), team)
        has_opp = same(r.get("home"), opponent) or same(r.get("away"), opponent)
        if has_team and has_opp:
            return r
    return None

def result_for_team(result, team):
    if not result:
        return None
    hs, as_ = int(result["homeScore"]), int(result["awayScore"])
    if same(result["home"], team):
        return "W" if hs > as_ else "L"
    if same(result["away"], team):
        return "W" if as_ > hs else "L"
    return None

def evaluate(schedule, results, pick, week):
    if not pick or not pick.get("team"):
        return "no-pick", 0, 0
    tw = get_team_week(schedule, pick["team"], week)
    if not tw:
        return "invalid", 0, 0
    if not tw.get("eligible"):
        return "ineligible", 0, 0
    wins = 1 if week == 1 else 0
    losses = 0
    for g in tw["games"]:
        outcome = result_for_team(find_result(results, g["date"], pick["team"], g["opponent"]), pick["team"])
        if outcome == "W": wins += 1
        if outcome == "L": losses += 1
    if losses >= 2: return "eliminated", wins, losses
    if losses == 1: return "strike", wins, losses
    return "safe", wins, losses

def main():
    players = load("players.json")
    picks = load("picks.json")
    schedule = load("schedule.json")
    results = load("results.json")
    weeks = load("weeks.json")
    state = {p["name"]: {"alive": True, "strikes": 0, "used": []} for p in players}
    print("Week | Alive Start | Alive End | New Strikes | Eliminated | Most Picked")
    print("-----|-------------|-----------|-------------|------------|------------")
    for week in range(1, len(weeks)+1):
        alive_start = sum(1 for s in state.values() if s["alive"])
        eliminated, new_strikes, counts = [], [], {}
        for player, s in state.items():
            if not s["alive"]:
                continue
            pick = get_pick(picks, player, week)
            team = pick.get("team") if pick else None
            if team:
                s["used"].append(team)
                counts[team] = counts.get(team, 0) + 1
            status, wins, losses = evaluate(schedule, results, pick, week)
            if status in {"no-pick", "invalid", "ineligible", "eliminated"}:
                s["alive"] = False
                eliminated.append(player)
            elif status == "strike":
                s["strikes"] += 1
                new_strikes.append(player)
                if s["strikes"] >= MAX_STRIKES:
                    s["alive"] = False
                    eliminated.append(player)
        alive_end = sum(1 for s in state.values() if s["alive"])
        most = ", ".join(f"{team} ({count})" for team, count in sorted(counts.items(), key=lambda x: -x[1])[:3])
        print(f"{week:>4} | {alive_start:>11} | {alive_end:>9} | {len(new_strikes):>11} | {len(eliminated):>10} | {most}")

if __name__ == "__main__":
    main()
