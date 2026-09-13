import { describe, expect, it } from 'vitest';
import { bestPlayerInMatch, compositeScore, groupSquadByPosition, resultFor, topScorer } from './teamStats.js';

const squad = [
  { id: 'fwd', name: 'Dan Nine', position: 'FWD', shirtNumber: 9, goals: 5, assists: 1 },
  { id: 'gk', name: 'Ann Keeper', position: 'GK', shirtNumber: 1, goals: 0, assists: 0 },
  { id: 'def', name: 'Ben Back', position: 'DEF', shirtNumber: 4, goals: 1, assists: 2 },
  { id: 'mid', name: 'Cal Mid', position: 'MID', shirtNumber: 8, goals: 5, assists: 6 },
  { id: 'def2', name: 'Eli Wide', position: 'DEF', shirtNumber: 2, goals: 0, assists: 0 },
];

const home = { id: 'home', name: 'Home FC', crest: { code: 'HOM', color: '#000000' } };
const away = { id: 'away', name: 'Away FC', crest: { code: 'AWY', color: '#ffffff' } };

function match(homeScore, awayScore, playerRatings = []) {
  return { id: 'm1', homeTeamId: 'home', awayTeamId: 'away', homeTeam: home, awayTeam: away, homeScore, awayScore, playerRatings };
}

describe('compositeScore', () => {
  it('applies the spec formula: goals×4 + assists×3 + rating×2 + minutes/90', () => {
    expect(compositeScore({ goals: 2, assists: 1, rating: 8, minutesPlayed: 90 })).toBe(28);
    expect(compositeScore({ goals: 0, assists: 0, rating: 6.5, minutesPlayed: 45 })).toBe(13.5);
  });

  it('accepts custom weights', () => {
    const weights = { goals: 1, assists: 1, rating: 0, per90Minutes: 0 };
    expect(compositeScore({ goals: 2, assists: 3, rating: 9, minutesPlayed: 90 }, weights)).toBe(5);
  });
});

describe('topScorer', () => {
  it('returns the player with most goals, breaking ties by assists', () => {
    expect(topScorer(squad).id).toBe('mid');
  });

  it('returns null when nobody has scored', () => {
    expect(topScorer(squad.map((p) => ({ ...p, goals: 0 })))).toBeNull();
    expect(topScorer([])).toBeNull();
  });
});

describe('bestPlayerInMatch', () => {
  it('picks the highest composite score among the squad only', () => {
    const result = bestPlayerInMatch(
      match(2, 1, [
        { playerId: 'fwd', goals: 1, assists: 0, rating: 7.5, minutesPlayed: 90 }, // 4 + 15 + 1 = 20
        { playerId: 'mid', goals: 0, assists: 2, rating: 8, minutesPlayed: 90 }, // 6 + 16 + 1 = 23
        { playerId: 'opponent', goals: 3, assists: 0, rating: 9.5, minutesPlayed: 90 },
      ]),
      squad,
    );
    expect(result.player.id).toBe('mid');
    expect(result.score).toBe(23);
    expect(result.stats.assists).toBe(2);
  });

  it('returns null when no squad player featured', () => {
    expect(bestPlayerInMatch(match(0, 0), squad)).toBeNull();
  });
});

describe('resultFor', () => {
  it('describes a home win', () => {
    expect(resultFor(match(3, 1), 'home')).toEqual({ isHome: true, goalsFor: 3, goalsAgainst: 1, outcome: 'W', opponent: away });
  });

  it('describes the same match as an away loss', () => {
    expect(resultFor(match(3, 1), 'away')).toEqual({ isHome: false, goalsFor: 1, goalsAgainst: 3, outcome: 'L', opponent: home });
  });

  it('describes a draw', () => {
    expect(resultFor(match(2, 2), 'away').outcome).toBe('D');
  });
});

describe('groupSquadByPosition', () => {
  it('groups GK, DEF, MID, FWD in order, sorted by shirt number', () => {
    const groups = groupSquadByPosition(squad);
    expect(groups.map((g) => g.key)).toEqual(['GK', 'DEF', 'MID', 'FWD']);
    expect(groups[1].players.map((p) => p.id)).toEqual(['def2', 'def']);
  });
});
