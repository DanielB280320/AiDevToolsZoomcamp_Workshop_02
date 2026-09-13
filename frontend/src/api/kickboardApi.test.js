import { describe, expect, it } from 'vitest';
import { ApiError, getLeagues, getStandings, getTeamDetail } from './kickboardApi.js';

describe('getLeagues', () => {
  it('returns the 9 competitions from the spec, grouped by region', async () => {
    const leagues = await getLeagues();
    expect(leagues).toHaveLength(9);

    const inRegion = (region) => leagues.filter((l) => l.region === region);
    expect(inRegion('Europe')).toHaveLength(4);
    expect(inRegion('Americas')).toHaveLength(4);
    expect(inRegion('Continental').map((l) => l.name)).toEqual(['UEFA Champions League']);

    for (const league of leagues) {
      expect(league).toEqual({
        id: expect.any(String),
        name: expect.any(String),
        country: expect.any(String),
        region: expect.any(String),
        code: expect.stringMatching(/^[A-Z]{3}$/),
        logo: expect.stringMatching(/^https:\/\/\S+\.png\/small$/),
        logoBackground: expect.stringMatching(/^#[0-9a-f]{6}$/i),
        season: expect.any(String),
        color: expect.stringMatching(/^#[0-9a-f]{6}$/i),
      });
    }
  });

  it('returns copies, so callers cannot corrupt the data', async () => {
    const first = await getLeagues();
    first[0].name = 'Changed';
    const second = await getLeagues();
    expect(second[0].name).toBe('Premier League');
  });
});

describe('getStandings', () => {
  it('returns a consistent, ordered table for every league', async () => {
    for (const league of await getLeagues()) {
      const standings = await getStandings(league.id);
      expect(standings.league).toEqual(league);
      expect(standings.teams.map((t) => t.position)).toEqual(standings.teams.map((_, i) => i + 1));

      standings.teams.forEach((team, i) => {
        expect(team.leagueId).toBe(league.id);
        expect(team.crest.logo).toMatch(/^https:\/\/\S+\.png(\/small)?$/);
        expect(team.wins + team.draws + team.losses).toBe(team.played);
        expect(team.points).toBe(team.wins * 3 + team.draws);
        expect(team.goalDifference).toBe(team.goalsFor - team.goalsAgainst);
        if (i > 0) expect(team.points).toBeLessThanOrEqual(standings.teams[i - 1].points);
      });
    }
  });

  it('rejects unknown leagues with a 404', async () => {
    await expect(getStandings('no-such-league')).rejects.toBeInstanceOf(ApiError);
    await expect(getStandings('no-such-league')).rejects.toMatchObject({ status: 404, message: 'League not found' });
  });
});

describe('getTeamDetail', () => {
  it('returns the team, its league, squad and last 5 results', async () => {
    const { teams } = await getStandings('premier-league');
    const liverpool = teams.find((t) => t.name === 'Liverpool');

    const detail = await getTeamDetail(liverpool.id);

    expect(detail.team).toEqual(liverpool);
    expect(detail.league.id).toBe('premier-league');
    expect(new Set(detail.squad.map((p) => p.position))).toEqual(new Set(['GK', 'DEF', 'MID', 'FWD']));
    expect(detail.squad.every((p) => p.teamId === liverpool.id)).toBe(true);

    expect(detail.recentMatches).toHaveLength(5);
    const dates = detail.recentMatches.map((m) => m.date);
    expect(dates).toEqual([...dates].sort().reverse());
    for (const match of detail.recentMatches) {
      expect([match.homeTeam.id, match.awayTeam.id]).toContain(liverpool.id);
    }
  });

  it("matches the team's goals to its players' goals", async () => {
    const { teams } = await getStandings('bundesliga');
    for (const team of teams) {
      const { squad, recentMatches } = await getTeamDetail(team.id);
      const squadIds = new Set(squad.map((p) => p.id));

      expect(squad.reduce((sum, p) => sum + p.goals, 0)).toBe(team.goalsFor);

      for (const match of recentMatches) {
        const teamGoals = match.homeTeamId === team.id ? match.homeScore : match.awayScore;
        const playerGoals = match.playerRatings
          .filter((entry) => squadIds.has(entry.playerId))
          .reduce((sum, entry) => sum + entry.goals, 0);
        expect(playerGoals).toBe(teamGoals);
      }
    }
  });

  it('rejects unknown teams with a 404', async () => {
    await expect(getTeamDetail('no-such-team')).rejects.toMatchObject({ status: 404, message: 'Team not found' });
  });
});
