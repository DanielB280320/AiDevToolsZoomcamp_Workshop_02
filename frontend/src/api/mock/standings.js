function emptyRow(team) {
  return { ...team, played: 0, wins: 0, draws: 0, losses: 0, goalsFor: 0, goalsAgainst: 0 };
}

function record(row, scored, conceded) {
  row.played += 1;
  row.goalsFor += scored;
  row.goalsAgainst += conceded;
  if (scored > conceded) row.wins += 1;
  else if (scored < conceded) row.losses += 1;
  else row.draws += 1;
}

// Points, then goal difference, then goals scored, then name.
function compareRows(a, b) {
  return (
    b.points - a.points ||
    b.goalDifference - a.goalDifference ||
    b.goalsFor - a.goalsFor ||
    a.name.localeCompare(b.name)
  );
}

/** Builds the league table (Team rows with position, W/D/L, GD, points) from played matches. */
export function computeStandings(teams, matches) {
  const rows = new Map(teams.map((team) => [team.id, emptyRow(team)]));

  for (const match of matches) {
    const home = rows.get(match.homeTeamId);
    const away = rows.get(match.awayTeamId);
    if (!home || !away) {
      throw new Error(`Match ${match.id} references a team outside this league`);
    }
    record(home, match.homeScore, match.awayScore);
    record(away, match.awayScore, match.homeScore);
  }

  return [...rows.values()]
    .map((row) => ({
      ...row,
      goalDifference: row.goalsFor - row.goalsAgainst,
      points: row.wins * 3 + row.draws,
    }))
    .sort(compareRows)
    .map((row, index) => ({ ...row, position: index + 1 }));
}
