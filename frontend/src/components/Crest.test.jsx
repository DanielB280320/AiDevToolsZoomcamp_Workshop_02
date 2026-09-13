import { fireEvent, render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Crest } from './Crest.jsx';

const crest = { code: 'LIV', color: '#C8102E', logo: 'https://example.com/liverpool.png' };

describe('Crest', () => {
  it('shows the club logo when there is one', () => {
    const { container } = render(<Crest crest={crest} />);
    expect(container.querySelector('img')).toHaveAttribute('src', crest.logo);
  });

  it('falls back to the coloured code badge when the logo fails to load', () => {
    const { container } = render(<Crest crest={crest} />);

    fireEvent.error(container.querySelector('img'));

    expect(container.querySelector('img')).toBeNull();
    expect(container).toHaveTextContent('LIV');
  });

  it('shows the badge when there is no logo', () => {
    const { container } = render(<Crest crest={{ code: 'ARS', color: '#EF0107' }} />);
    expect(container.querySelector('img')).toBeNull();
    expect(container).toHaveTextContent('ARS');
  });

  it('tries a different logo even after a previous one failed', () => {
    const { container, rerender } = render(<Crest crest={crest} />);
    fireEvent.error(container.querySelector('img'));

    rerender(<Crest crest={{ ...crest, logo: 'https://example.com/other.png' }} />);

    expect(container.querySelector('img')).toHaveAttribute('src', 'https://example.com/other.png');
  });
});
