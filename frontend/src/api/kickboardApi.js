/**
 * Kickboard API client — the ONLY module the UI uses to talk to the backend.
 *
 * Every call is currently served by the in-memory mock backend in ./mock. To connect a
 * real backend, replace `request` with a `fetch` to the matching endpoint; components and
 * hooks don't need to change as long as the response shapes stay the same:
 *
 *   getLeagues()            GET /api/leagues                  -> League[]
 *   getStandings(leagueId)  GET /api/leagues/:leagueId/standings -> { league, teams: Team[] }
 *   getTeamDetail(teamId)   GET /api/teams/:teamId            -> { team, league, squad, recentMatches }
 *
 * Failures reject with an ApiError carrying an HTTP-style `status`.
 */
import { ApiError } from './errors.js';
import * as mockBackend from './mock/mockBackend.js';

const MOCK_LATENCY_MS = import.meta.env.MODE === 'test' ? 0 : 250;

async function request(handler) {
  await new Promise((resolve) => setTimeout(resolve, MOCK_LATENCY_MS));
  // Clone so callers can't mutate the mock "database", just like a real network response.
  return structuredClone(handler());
}

export function getLeagues() {
  return request(() => mockBackend.listLeagues());
}

export function getStandings(leagueId) {
  return request(() => mockBackend.getLeagueStandings(leagueId));
}

export function getTeamDetail(teamId) {
  return request(() => mockBackend.getTeamDetail(teamId));
}

export { ApiError };
