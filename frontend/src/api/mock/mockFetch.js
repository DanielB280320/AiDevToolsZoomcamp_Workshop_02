// A `fetch` stand-in that serves the backend's routes from the in-memory mock, so tests run
// without a live server. Installed globally in src/test/setup.js.
import * as mockBackend from './mockBackend.js';

const routes = [
  [/^\/api\/leagues$/, () => mockBackend.listLeagues()],
  [/^\/api\/leagues\/([^/]+)\/standings$/, (leagueId) => mockBackend.getLeagueStandings(leagueId)],
  [/^\/api\/teams\/([^/]+)$/, (teamId) => mockBackend.getTeamDetail(teamId)],
];

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export async function mockFetch(input) {
  const { pathname } = new URL(input instanceof Request ? input.url : String(input));
  for (const [pattern, handler] of routes) {
    const match = pathname.match(pattern);
    if (!match) continue;
    try {
      return json(200, handler(...match.slice(1).map(decodeURIComponent)));
    } catch (error) {
      if (error.status) return json(error.status, { detail: error.message });
      throw error;
    }
  }
  return json(404, { detail: 'Not Found' });
}
