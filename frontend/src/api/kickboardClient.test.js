import { describe, expect, it } from 'vitest';
import { API_BASE_URL, ApiError, getLeagues, getStandings, getTeamDetail } from './kickboardApi.js';

describe('kickboardApi HTTP client', () => {
  it('defaults to the local backend', () => {
    expect(API_BASE_URL).toBe('http://localhost:8000');
  });

  it('requests the documented endpoints, encoding ids', async () => {
    await getLeagues();
    await getStandings('premier-league');
    await getTeamDetail('premier-league--liverpool');
    await getTeamDetail('a/b').catch(() => {});

    expect(fetch.mock.calls.map(([url]) => url)).toEqual([
      'http://localhost:8000/api/leagues',
      'http://localhost:8000/api/leagues/premier-league/standings',
      'http://localhost:8000/api/teams/premier-league--liverpool',
      'http://localhost:8000/api/teams/a%2Fb',
    ]);
  });

  it('turns error responses into an ApiError with the detail message', async () => {
    fetch.mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Team not found' }), { status: 404 }));
    await expect(getTeamDetail('x')).rejects.toMatchObject({ status: 404, message: 'Team not found' });
  });

  it('falls back to a generic message when the error body is not JSON', async () => {
    fetch.mockResolvedValueOnce(new Response('Internal Server Error', { status: 500 }));
    await expect(getLeagues()).rejects.toMatchObject({ status: 500, message: 'Request failed (500)' });
  });

  it('rejects with status 0 when the server is unreachable', async () => {
    fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    const error = await getLeagues().catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 0, message: 'Could not reach the Kickboard server.' });
  });
});
