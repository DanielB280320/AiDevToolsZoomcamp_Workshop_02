// In-memory stand-in for the backend, used by tests via mockFetch.js. The app talks to the real backend.
import { ApiError } from '../errors.js';
import { buildDataset } from './generate.js';

const RECENT_MATCHES = 5;

let dataset = null;

function db() {
  dataset ??= buildDataset();
  return dataset;
}

function findLeague(leagueId) {
  const league = db().leagues.find((l) => l.id === leagueId);
  if (!league) throw new ApiError(404, 'League not found');
  return league;
}

const teamSummary = ({ id, name, crest }) => ({ id, name, crest });

export function listLeagues() {
  return db().leagues;
}

export function getLeagueStandings(leagueId) {
  const league = findLeague(leagueId);
  const teams = db()
    .teams.filter((team) => team.leagueId === leagueId)
    .sort((a, b) => a.position - b.position);
  return { league, teams };
}

export function getTeamDetail(teamId) {
  const { teams, players, matches } = db();
  const team = teams.find((t) => t.id === teamId);
  if (!team) throw new ApiError(404, 'Team not found');

  const teamsById = new Map(teams.map((t) => [t.id, t]));
  const recentMatches = matches
    .filter((m) => m.homeTeamId === teamId || m.awayTeamId === teamId)
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, RECENT_MATCHES)
    .map((m) => ({
      ...m,
      homeTeam: teamSummary(teamsById.get(m.homeTeamId)),
      awayTeam: teamSummary(teamsById.get(m.awayTeamId)),
    }));

  return {
    team,
    league: findLeague(team.leagueId),
    squad: players.filter((p) => p.teamId === teamId),
    recentMatches,
  };
}
