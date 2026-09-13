import { fireEvent, render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LeagueLogo } from './LeagueLogo.jsx';

const league = { code: 'ENG', color: '#3D1159', logo: 'https://example.com/premier-league.png' };

describe('LeagueLogo', () => {
  it('shows the league badge when there is one', () => {
    const { container } = render(<LeagueLogo league={league} />);
    expect(container.querySelector('img')).toHaveAttribute('src', league.logo);
    expect(container).not.toHaveTextContent('ENG');
  });

  it('puts the badge on the league-specific tile colour', () => {
    const { container } = render(<LeagueLogo league={{ ...league, logoBackground: '#0B1F63' }} />);
    expect(container.firstChild.style.getPropertyValue('--tile')).toBe('#0B1F63');
  });

  it('falls back to the league code when the badge fails to load', () => {
    const { container } = render(<LeagueLogo league={league} />);

    fireEvent.error(container.querySelector('img'));

    expect(container.querySelector('img')).toBeNull();
    expect(container.firstChild).toHaveClass('league-logo--fallback');
    expect(container).toHaveTextContent('ENG');
  });

  it('shows the league code when there is no badge', () => {
    const { container } = render(<LeagueLogo league={{ code: 'UCL', color: '#0B1F63' }} size="lg" />);
    expect(container.firstChild).toHaveClass('league-logo--lg', 'league-logo--fallback');
    expect(container).toHaveTextContent('UCL');
  });
});
