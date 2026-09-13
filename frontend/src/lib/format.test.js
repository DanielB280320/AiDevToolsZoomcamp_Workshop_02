import { describe, expect, it } from 'vitest';
import { formatGoalDifference, formatMatchDate, ordinal, plural } from './format.js';

describe('ordinal', () => {
  it.each([
    [1, '1st'], [2, '2nd'], [3, '3rd'], [4, '4th'], [11, '11th'], [12, '12th'],
    [13, '13th'], [21, '21st'], [22, '22nd'], [101, '101st'], [111, '111th'],
  ])('%i -> %s', (n, expected) => {
    expect(ordinal(n)).toBe(expected);
  });
});

describe('formatGoalDifference', () => {
  it('signs positive and negative values', () => {
    expect(formatGoalDifference(5)).toBe('+5');
    expect(formatGoalDifference(0)).toBe('0');
    expect(formatGoalDifference(-3)).toBe('−3');
  });
});

describe('plural', () => {
  it('pluralises all counts except one', () => {
    expect(plural(1, 'goal')).toBe('1 goal');
    expect(plural(0, 'goal')).toBe('0 goals');
    expect(plural(7, 'goal')).toBe('7 goals');
  });
});

describe('formatMatchDate', () => {
  it('formats ISO dates without shifting the day', () => {
    expect(formatMatchDate('2026-09-12')).toBe('12 Sept 2026');
  });
});
