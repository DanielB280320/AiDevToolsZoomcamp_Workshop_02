export const POSITIONS = [
  { key: 'GK', label: 'Goalkeepers' },
  { key: 'DEF', label: 'Defenders' },
  { key: 'MID', label: 'Midfielders' },
  { key: 'FWD', label: 'Forwards' },
];

// Placeholder weights from the spec; tune once real match data is available.
export const COMPOSITE_WEIGHTS = { goals: 4, assists: 3, rating: 2, per90Minutes: 1 };

export function compositeScore({ goals, assists, rating, minutesPlayed }, weights = COMPOSITE_WEIGHTS) {
  return (
    goals * weights.goals +
    assists * weights.assists +
    rating * weights.rating +
    (minutesPlayed / 90) * weights.per90Minutes
  );
}

/** Player with the most goals (ties broken by assists), or null if nobody has scored. */
export function topScorer(squad) {
  let best = null;
  for (const player of squad) {
    if (player.goals === 0) continue;
    if (!best || player.goals > best.goals || (player.goals === best.goals && player.assists > best.assists)) {
      best = player;
    }
  }
  return best;
}

/** Highest composite score among this squad's players in the match, or null if none played. */
export function bestPlayerInMatch(match, squad) {
  const squadById = new Map(squad.map((p) => [p.id, p]));
  let best = null;
  for (const stats of match.playerRatings) {
    const player = squadById.get(stats.playerId);
    if (!player) continue;
    const score = compositeScore(stats);
    if (!best || score > best.score) best = { player, stats, score };
  }
  return best;
}

/** The match from the team's point of view. */
export function resultFor(match, teamId) {
  const isHome = match.homeTeamId === teamId;
  const goalsFor = isHome ? match.homeScore : match.awayScore;
  const goalsAgainst = isHome ? match.awayScore : match.homeScore;
  const outcome = goalsFor > goalsAgainst ? 'W' : goalsFor < goalsAgainst ? 'L' : 'D';
  return { isHome, goalsFor, goalsAgainst, outcome, opponent: isHome ? match.awayTeam : match.homeTeam };
}

export function groupSquadByPosition(squad) {
  return POSITIONS.map((position) => ({
    ...position,
    players: squad
      .filter((p) => p.position === position.key)
      .sort(byShirtNumber),
  }));
}

/** Shirt number ascending; players without one (live data can omit it) go last, by name. */
function byShirtNumber(a, b) {
  return (a.shirtNumber ?? Infinity) - (b.shirtNumber ?? Infinity) || a.name.localeCompare(b.name);
}
