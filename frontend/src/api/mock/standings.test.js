import { describe, expect, it } from 'vitest';
import { computeStandings } from './standings.js';

const team = (id) => ({ id, name: id.toUpperCase(), leagueId: 'test' });
const game = (homeTeamId, homeScore, awayScore, awayTeamId) => ({
  id: `${homeTeamId}-${awayTeamId}`,
  homeTeamId,
  awayTeamId,
  homeScore,
  awayScore,
});

const byId = (rows) => Object.fromEntries(rows.map((row) => [row.id, row]));

describe('computeStandings', () => {
  it('tallies played, W/D/L, goal difference and points', () => {
    const rows = byId(
      computeStandings([team('a'), team('b'), team('c')], [game('a', 2, 0, 'b'), game('b', 1, 1, 'c'), game('c', 0, 3, 'a')]),
    );

    expect(rows.a).toMatchObject({ position: 1, played: 2, wins: 2, draws: 0, losses: 0, goalDifference: 5, points: 6 });
    expect(rows.b).toMatchObject({ position: 2, played: 2, wins: 0, draws: 1, losses: 1, goalDifference: -2, points: 1 });
    expect(rows.c).toMatchObject({ position: 3, played: 2, wins: 0, draws: 1, losses: 1, goalDifference: -3, points: 1 });
  });

  it('breaks points ties on goal difference, then goals scored', () => {
    const byGoalDifference = computeStandings(
      [team('a'), team('b'), team('c')],
      [game('b', 1, 0, 'c'), game('a', 3, 0, 'c'), game('a', 1, 1, 'b')],
    );
    expect(byGoalDifference.map((r) => r.id)).toEqual(['a', 'b', 'c']);

    const byGoalsScored = computeStandings(
      [team('e'), team('d'), team('f')],
      [game('e', 1, 0, 'f'), game('d', 3, 2, 'f'), game('d', 0, 0, 'e')],
    );
    expect(byGoalsScored.map((r) => r.id)).toEqual(['d', 'e', 'f']);
  });

  it('lists teams without matches with zeroed stats, ordered by name', () => {
    const rows = computeStandings([team('b'), team('a')], []);
    expect(rows.map((r) => r.id)).toEqual(['a', 'b']);
    expect(rows[0]).toMatchObject({ played: 0, points: 0, goalDifference: 0, position: 1 });
  });

  it('rejects matches involving unknown teams', () => {
    expect(() => computeStandings([team('a')], [game('a', 1, 0, 'zzz')])).toThrow(/outside this league/);
  });
});
