/**
 * Kickboard API client — the ONLY module the UI uses to talk to the backend.
 *
 * Calls the Kickboard backend (see openapi.yaml) at VITE_API_BASE_URL, defaulting to
 * http://localhost:8000:
 *
 *   getLeagues()            GET /api/leagues                  -> League[]
 *   getStandings(leagueId)  GET /api/leagues/:leagueId/standings -> { league, teams: Team[] }
 *   getTeamDetail(teamId)   GET /api/teams/:teamId            -> { team, league, squad, recentMatches }
 *
 * Failures reject with an ApiError carrying the HTTP `status` (0 when the server can't be reached).
 */
import { ApiError } from './errors.js';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

async function request(path) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { headers: { Accept: 'application/json' } });
  } catch {
    throw new ApiError(0, 'Could not reach the Kickboard server.');
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export function getLeagues() {
  return request('/api/leagues');
}

export function getStandings(leagueId) {
  return request(`/api/leagues/${encodeURIComponent(leagueId)}/standings`);
}

export function getTeamDetail(teamId) {
  return request(`/api/teams/${encodeURIComponent(teamId)}`);
}

export { ApiError };
