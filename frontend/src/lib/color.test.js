import { describe, expect, it } from 'vitest';
import { readableTextColor } from './color.js';

describe('readableTextColor', () => {
  it('uses dark text on light colours', () => {
    expect(readableTextColor('#FFE667')).toBe('#111418');
    expect(readableTextColor('#ffffff')).toBe('#111418');
  });

  it('uses white text on dark colours', () => {
    expect(readableTextColor('#034694')).toBe('#ffffff');
    expect(readableTextColor('#C8102E')).toBe('#ffffff');
  });
});
