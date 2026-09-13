import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import App from './App.jsx';

function goTo(path) {
  window.history.replaceState(null, '', path);
}

async function findStandings(leagueName) {
  return screen.findByRole('table', { name: `${leagueName} standings` });
}

describe('App', () => {
  beforeEach(() => goTo('/'));

  it('lists all leagues and shows the first league by default', async () => {
    render(<App />);

    const nav = screen.getByRole('navigation', { name: 'Leagues' });
    expect(await within(nav).findAllByRole('button')).toHaveLength(9);
    expect(within(nav).getByRole('heading', { name: 'Europe' })).toBeInTheDocument();
    expect(within(nav).getByRole('heading', { name: 'Americas' })).toBeInTheDocument();
    expect(within(nav).getByRole('heading', { name: 'Continental' })).toBeInTheDocument();

    const table = await findStandings('Premier League');
    expect(screen.getByRole('heading', { level: 1, name: 'Premier League' })).toBeInTheDocument();
    // header row + 10 teams
    expect(within(table).getAllByRole('row')).toHaveLength(11);
    expect(within(table).getByRole('columnheader', { name: 'Points' })).toBeInTheDocument();
  });

  it('switches league from the sidebar', async () => {
    const user = userEvent.setup();
    render(<App />);
    await findStandings('Premier League');

    await user.click(screen.getByRole('button', { name: 'La Liga' }));

    const table = await findStandings('La Liga');
    expect(within(table).getByRole('button', { name: 'Barcelona' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'La Liga' })).toHaveAttribute('aria-current', 'page');
    expect(window.location.hash).toBe('#/leagues/la-liga');
  });

  it('opens team details from the table and closes them with the close button', async () => {
    const user = userEvent.setup();
    render(<App />);
    const table = await findStandings('Premier League');

    await user.click(within(table).getByRole('button', { name: 'Arsenal' }));

    const panel = screen.getByRole('complementary', { name: 'Team details' });
    expect(await within(panel).findByRole('heading', { level: 2, name: 'Arsenal' })).toBeInTheDocument();
    expect(window.location.hash).toBe('#/leagues/premier-league/teams/premier-league--arsenal');

    expect(within(panel).getByRole('region', { name: 'Top scorer' })).toHaveTextContent(/\d+ goals?/);
    expect(within(panel).getByRole('region', { name: 'Best player in last match' })).toHaveTextContent(/Rating/);

    const results = within(panel).getByRole('list', { name: 'Recent results' });
    expect(within(results).getAllByRole('listitem')).toHaveLength(5);

    for (const group of ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']) {
      expect(within(within(panel).getByRole('list', { name: group })).getAllByRole('listitem').length).toBeGreaterThan(0);
    }

    await user.click(within(panel).getByRole('button', { name: 'Close team details' }));
    expect(screen.queryByRole('complementary', { name: 'Team details' })).not.toBeInTheDocument();
    expect(window.location.hash).toBe('#/leagues/premier-league');
  });

  it('opens a team by clicking anywhere on its row and closes with Escape', async () => {
    const user = userEvent.setup();
    render(<App />);
    const table = await findStandings('Premier League');

    const chelseaRow = within(table).getByRole('button', { name: 'Chelsea' }).closest('tr');
    await user.click(chelseaRow.lastElementChild);

    expect(await screen.findByRole('heading', { level: 2, name: 'Chelsea' })).toBeInTheDocument();
    expect(chelseaRow).toHaveClass('is-selected');

    await user.keyboard('{Escape}');
    expect(screen.queryByRole('complementary', { name: 'Team details' })).not.toBeInTheDocument();
  });

  it('restores the league and team from the URL', async () => {
    goTo('/#/leagues/serie-a/teams/serie-a--napoli');
    render(<App />);

    expect(await findStandings('Serie A')).toBeInTheDocument();
    const panel = screen.getByRole('complementary', { name: 'Team details' });
    expect(await within(panel).findByRole('heading', { level: 2, name: 'Napoli' })).toBeInTheDocument();
    expect(within(panel).getByText(/Serie A · \d+(st|nd|rd|th) · \d+ pts?/)).toBeInTheDocument();
  });

  it('shows an error for an unknown league', async () => {
    goTo('/#/leagues/not-a-league');
    render(<App />);

    expect(await screen.findByRole('alert')).toHaveTextContent('League not found');
  });

  it('shows an error for an unknown team', async () => {
    goTo('/#/leagues/mls/teams/not-a-team');
    render(<App />);

    const panel = screen.getByRole('complementary', { name: 'Team details' });
    expect(await within(panel).findByRole('alert')).toHaveTextContent('Team not found');
  });
});
