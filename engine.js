const MAX_STRIKES = 3;

function norm(value) {
  return String(value || "").toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, " ").trim();
}

function sameTeam(a, b) {
  return norm(a) === norm(b);
}

function getPick(picks, player, week) {
  return picks.find(p => sameTeam(p.player, player.name) && Number(p.week) === Number(week));
}

function getTeamWeek(schedule, team, week) {
  return schedule.find(s => sameTeam(s.team, team) && Number(s.week) === Number(week));
}

function findResult(results, date, team, opponent) {
  return results.find(r => {
    if (r.date !== date) return false;
    const hasTeam = sameTeam(r.home, team) || sameTeam(r.away, team);
    const hasOpp = sameTeam(r.home, opponent) || sameTeam(r.away, opponent);
    return hasTeam && hasOpp;
  });
}

function resultForTeam(result, team) {
  if (!result) return null;
  const homeScore = Number(result.homeScore);
  const awayScore = Number(result.awayScore);
  if (!Number.isFinite(homeScore) || !Number.isFinite(awayScore)) return null;
  if (sameTeam(result.home, team)) return homeScore > awayScore ? "W" : "L";
  if (sameTeam(result.away, team)) return awayScore > homeScore ? "W" : "L";
  return null;
}

function evaluatePick({ schedule, results, pick, week }) {
  if (!pick || !pick.team) return { status: "no-pick", wins: 0, losses: 0, games: [] };
  const teamWeek = getTeamWeek(schedule, pick.team, week);
  if (!teamWeek) return { status: "invalid", wins: 0, losses: 0, games: [], note: "Team not found in schedule for this week." };
  if (!teamWeek.eligible) return { status: "ineligible", wins: 0, losses: 0, games: teamWeek.games, note: "Team had only one game this week." };

  let wins = week === 1 ? 1 : 0; // ghost midweek win
  let losses = 0;
  const games = teamWeek.games.map(g => {
    const result = findResult(results, g.date, pick.team, g.opponent);
    const outcome = resultForTeam(result, pick.team);
    if (outcome === "W") wins += 1;
    if (outcome === "L") losses += 1;
    return { ...g, result, outcome };
  });

  if (losses >= 2) return { status: "eliminated", wins, losses, games };
  if (losses === 1) return { status: "strike", wins, losses, games };
  return { status: "safe", wins, losses, games };
}

function simulateThroughWeek({ players, picks, schedule, results, throughWeek }) {
  const state = players.map(p => ({
    ...p,
    alive: true,
    strikes: 0,
    usedTeams: [],
    history: []
  }));

  const weeklyStories = [];
  for (let week = 1; week <= throughWeek; week++) {
    const story = { week, aliveStart: state.filter(p => p.alive).length, eliminated: [], newStrikes: [], picksByTeam: {}, outcomes: [] };

    for (const player of state) {
      if (!player.alive) continue;
      const pick = getPick(picks, player, week);
      const evaln = evaluatePick({ schedule, results, pick, week });
      if (pick?.team) {
        player.usedTeams.push(pick.team);
        story.picksByTeam[pick.team] = (story.picksByTeam[pick.team] || 0) + 1;
      }

      const entry = { week, pick: pick?.team || null, outcome: evaln.status, wins: evaln.wins, losses: evaln.losses, games: evaln.games };
      player.history.push(entry);
      story.outcomes.push({ player: player.name, ...entry });

      if (["no-pick", "invalid", "ineligible", "eliminated"].includes(evaln.status)) {
        player.alive = false;
        player.eliminatedWeek = week;
        story.eliminated.push(player.name);
      } else if (evaln.status === "strike") {
        player.strikes += 1;
        story.newStrikes.push(player.name);
        if (player.strikes >= MAX_STRIKES) {
          player.alive = false;
          player.eliminatedWeek = week;
          story.eliminated.push(player.name);
        }
      }
    }
    story.aliveEnd = state.filter(p => p.alive).length;
    story.mostPicked = Object.entries(story.picksByTeam).sort((a,b) => b[1]-a[1]).slice(0,5).map(([team,count]) => ({team,count}));
    weeklyStories.push(story);
  }
  return { players: state, weeklyStories };
}

if (typeof module !== "undefined") {
  module.exports = { simulateThroughWeek, evaluatePick, norm, sameTeam };
}
