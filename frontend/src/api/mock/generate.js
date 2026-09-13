import { CLUBS, LEAGUES, NAME_POOLS } from './fixtures.js';
import { createRng } from './random.js';
import { computeStandings } from './standings.js';

const SQUAD_SHIRTS = {
  GK: [1, 13],
  DEF: [2, 3, 4, 5, 15, 22],
  MID: [6, 8, 10, 14, 16, 18],
  FWD: [7, 9, 11, 19],
};
const LINEUP = { GK: 1, DEF: 4, MID: 3, FWD: 3 };
const SUBSTITUTIONS = 3;
const SCORER_WEIGHT = { GK: 0, DEF: 1, MID: 3, FWD: 6 };
const ASSIST_WEIGHT = { GK: 0, DEF: 2, MID: 4, FWD: 3 };
const ASSIST_CHANCE = 0.75;

const LAST_MATCHDAY = Date.UTC(2026, 8, 12);
const DAYS_BETWEEN_ROUNDS = 5;
const DAY_MS = 86_400_000;

// Seeded by club, so a club has the same player names in every competition it plays.
function clubRoster(clubId) {
  const { first, last } = NAME_POOLS[CLUBS[clubId].namePool];
  const rng = createRng(`roster:${clubId}`);
  const usedNames = new Set();

  return Object.entries(SQUAD_SHIRTS).flatMap(([position, shirts]) =>
    shirts.map((shirtNumber) => {
      let name;
      do {
        name = `${rng.pick(first)} ${rng.pick(last)}`;
      } while (usedNames.has(name));
      usedNames.add(name);
      return { name, position, shirtNumber };
    }),
  );
}

/** Circle-method round robin: every team plays once per round and meets every other team once. */
export function roundRobin(teamIds) {
  const ids = teamIds.length % 2 ? [...teamIds, null] : [...teamIds];
  const rounds = [];

  for (let round = 0; round < ids.length - 1; round++) {
    const pairs = [];
    for (let i = 0; i < ids.length / 2; i++) {
      const a = ids[i];
      const b = ids[ids.length - 1 - i];
      if (a && b) pairs.push(round % 2 === 0 ? [a, b] : [b, a]);
    }
    rounds.push(pairs);
    ids.splice(1, 0, ids.pop());
  }
  return rounds;
}

function schedule(teamIds, format) {
  const firstLeg = roundRobin(teamIds);
  if (format === 'single') return firstLeg;
  const secondLeg = firstLeg.map((pairs) => pairs.map(([home, away]) => [away, home]));
  return [...firstLeg, ...secondLeg];
}

function simulateTeamPerformance(rng, squad, goalsFor, goalsAgainst) {
  const starters = Object.entries(LINEUP).flatMap(([position, count]) =>
    rng.shuffle(squad.filter((p) => p.position === position)).slice(0, count),
  );
  const bench = rng.shuffle(squad.filter((p) => p.position !== 'GK' && !starters.includes(p)));
  const subbedOff = rng.shuffle(starters.filter((p) => p.position !== 'GK')).slice(0, SUBSTITUTIONS);

  const minutes = new Map(starters.map((p) => [p.id, 90]));
  subbedOff.forEach((player, i) => {
    const minute = rng.int(55, 85);
    minutes.set(player.id, minute);
    minutes.set(bench[i].id, 90 - minute);
  });

  const onPitch = squad.filter((p) => minutes.has(p.id));
  const stats = new Map(onPitch.map((p) => [p.id, { goals: 0, assists: 0 }]));

  for (let goal = 0; goal < goalsFor; goal++) {
    const scorer = rng.weightedPick(onPitch, (p) => SCORER_WEIGHT[p.position] * minutes.get(p.id));
    stats.get(scorer.id).goals += 1;
    if (rng.next() < ASSIST_CHANCE) {
      const candidates = onPitch.filter((p) => p !== scorer);
      const assister = rng.weightedPick(candidates, (p) => ASSIST_WEIGHT[p.position] * minutes.get(p.id));
      stats.get(assister.id).assists += 1;
    }
  }

  const resultBonus = goalsFor > goalsAgainst ? 0.3 : goalsFor < goalsAgainst ? -0.3 : 0;

  return onPitch.map((player) => {
    const { goals, assists } = stats.get(player.id);
    const minutesPlayed = minutes.get(player.id);
    const cleanSheet = goalsAgainst === 0 && ['GK', 'DEF'].includes(player.position) ? 0.5 : 0;
    const cameo = minutesPlayed < 30 ? -0.4 : 0;
    const raw = 6 + rng.next() * 1.2 + goals * 0.9 + assists * 0.5 + resultBonus + cleanSheet + cameo;
    const rating = Math.round(Math.min(10, Math.max(4.5, raw)) * 10) / 10;
    return { playerId: player.id, goals, assists, rating, minutesPlayed };
  });
}

function generateLeague(league) {
  const rng = createRng(`league:${league.id}`);

  const teams = league.clubIds.map((clubId) => {
    const club = CLUBS[clubId];
    return {
      id: `${league.id}--${clubId}`,
      name: club.name,
      leagueId: league.id,
      crest: { code: club.code, color: club.color, logo: club.logo },
    };
  });
  const strength = new Map(teams.map((team, i) => [team.id, 1 - (i / teams.length) * 0.6]));

  const players = teams.flatMap((team, i) =>
    clubRoster(league.clubIds[i]).map((player) => ({
      id: `${team.id}--${player.shirtNumber}`,
      teamId: team.id,
      ...player,
      goals: 0,
      assists: 0,
    })),
  );
  const playersById = new Map(players.map((p) => [p.id, p]));
  const squads = new Map(teams.map((team) => [team.id, players.filter((p) => p.teamId === team.id)]));

  const rounds = schedule(teams.map((t) => t.id), league.format).slice(0, league.roundsPlayed);

  const matches = rounds.flatMap((pairs, roundIndex) => {
    const daysAgo = (rounds.length - 1 - roundIndex) * DAYS_BETWEEN_ROUNDS;
    const date = new Date(LAST_MATCHDAY - daysAgo * DAY_MS).toISOString().slice(0, 10);

    return pairs.map(([homeTeamId, awayTeamId], matchIndex) => {
      const edge = strength.get(homeTeamId) - strength.get(awayTeamId);
      const homeScore = rng.poisson(Math.max(0.25, 1.55 + edge * 1.6));
      const awayScore = rng.poisson(Math.max(0.25, 1.15 - edge * 1.6));
      const playerRatings = [
        ...simulateTeamPerformance(rng, squads.get(homeTeamId), homeScore, awayScore),
        ...simulateTeamPerformance(rng, squads.get(awayTeamId), awayScore, homeScore),
      ];

      for (const entry of playerRatings) {
        const player = playersById.get(entry.playerId);
        player.goals += entry.goals;
        player.assists += entry.assists;
      }

      return {
        id: `${league.id}--r${roundIndex + 1}-m${matchIndex + 1}`,
        leagueId: league.id,
        round: roundIndex + 1,
        homeTeamId,
        awayTeamId,
        homeScore,
        awayScore,
        date,
        playerRatings,
      };
    });
  });

  return { teams: computeStandings(teams, matches), players, matches };
}

/** Generates the whole mock database: leagues, teams (with standings), players and matches. */
export function buildDataset() {
  const generated = LEAGUES.map(generateLeague);
  return {
    leagues: LEAGUES.map(({ id, name, country, region, code, logo, logoBackground = '#ffffff', season, color }) => ({
      id, name, country, region, code, logo, logoBackground, season, color,
    })),
    teams: generated.flatMap((g) => g.teams),
    players: generated.flatMap((g) => g.players),
    matches: generated.flatMap((g) => g.matches),
  };
}
