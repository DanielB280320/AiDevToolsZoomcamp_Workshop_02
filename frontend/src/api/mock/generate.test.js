import { describe, expect, it } from 'vitest';
import { buildDataset, roundRobin } from './generate.js';

describe('roundRobin', () => {
  it.each([4, 5, 10])('with %i teams, every pair meets exactly once and nobody plays twice in a round', (count) => {
    const ids = Array.from({ length: count }, (_, i) => `t${i}`);
    const rounds = roundRobin(ids);
    const pairings = new Set();

    for (const round of rounds) {
      const playing = round.flat();
      expect(new Set(playing).size).toBe(playing.length);
      for (const [home, away] of round) pairings.add([home, away].sort().join('|'));
    }

    expect(pairings.size).toBe((count * (count - 1)) / 2);
    expect(rounds.flat()).toHaveLength((count * (count - 1)) / 2);
  });
});

describe('buildDataset', () => {
  it('is deterministic', () => {
    expect(buildDataset()).toEqual(buildDataset());
  });

  it('keeps player season totals consistent with match stats', () => {
    const { players, matches } = buildDataset();
    const goalsByPlayer = new Map();
    for (const match of matches) {
      for (const entry of match.playerRatings) {
        goalsByPlayer.set(entry.playerId, (goalsByPlayer.get(entry.playerId) ?? 0) + entry.goals);
      }
    }
    for (const player of players) {
      expect(player.goals).toBe(goalsByPlayer.get(player.id) ?? 0);
    }
  });

  it('generates sane per-match player stats', () => {
    const { matches } = buildDataset();
    for (const entry of matches.flatMap((m) => m.playerRatings)) {
      expect(entry.rating).toBeGreaterThanOrEqual(4.5);
      expect(entry.rating).toBeLessThanOrEqual(10);
      expect(entry.minutesPlayed).toBeGreaterThan(0);
      expect(entry.minutesPlayed).toBeLessThanOrEqual(90);
    }
  });
});
