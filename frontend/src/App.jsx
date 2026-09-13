import { useCallback } from 'react';
import { getLeagues, getStandings } from './api/kickboardApi.js';
import { LeagueLogo } from './components/LeagueLogo.jsx';
import { Sidebar } from './components/Sidebar.jsx';
import { StandingsTable } from './components/StandingsTable.jsx';
import { StatusMessage } from './components/StatusMessage.jsx';
import { TeamDetail } from './components/TeamDetail.jsx';
import { useAsync } from './hooks/useAsync.js';
import { useHashRoute } from './hooks/useHashRoute.js';

export default function App() {
  const [route, navigate] = useHashRoute();
  const leagues = useAsync(() => getLeagues(), []);

  const leagueId = route.leagueId ?? leagues.data?.[0]?.id ?? null;
  const { teamId } = route;
  const league = leagues.data?.find((l) => l.id === leagueId) ?? null;
  const standings = useAsync(leagueId ? () => getStandings(leagueId) : null, [leagueId]);

  const selectLeague = useCallback((id) => navigate({ leagueId: id, teamId: null }), [navigate]);
  const selectTeam = useCallback((id) => navigate({ leagueId, teamId: id }), [navigate, leagueId]);
  const closeTeam = useCallback(() => navigate({ leagueId, teamId: null }), [navigate, leagueId]);

  return (
    <div
      className={teamId ? 'app app--panel-open' : 'app'}
      style={league ? { '--league': league.color } : undefined}
    >
      <Sidebar
        leagues={leagues.data ?? []}
        status={leagues.status}
        error={leagues.error}
        onRetry={leagues.retry}
        selectedLeagueId={leagueId}
        onSelect={selectLeague}
      />

      <main className="main">
        <header className="page-header">
          {league && <LeagueLogo league={league} size="lg" />}
          <div>
            {league && (
              <p className="page-header__eyebrow">
                {league.country} · {league.season} season
              </p>
            )}
            <h1 className="page-header__title">{league?.name ?? 'Standings'}</h1>
            <p className="page-header__hint">Select a team to see its top scorer, standout player, form and squad.</p>
          </div>
        </header>

        {standings.status === 'loading' && <StatusMessage>Loading standings…</StatusMessage>}
        {standings.status === 'error' && <StatusMessage error={standings.error} onRetry={standings.retry} />}
        {standings.status === 'success' && (
          <StandingsTable
            league={standings.data.league}
            teams={standings.data.teams}
            selectedTeamId={teamId}
            onSelectTeam={selectTeam}
          />
        )}

        <p className="data-note">
          Sample data: clubs and logos are real, players and results are generated. Background photo:{' '}
          <a href="https://commons.wikimedia.org/wiki/File:Cape_Town_Stadium,_Cape_Town,_South_Africa_(Unsplash).jpg">
            Cape Town Stadium
          </a>{' '}
          by Deklerk Basson (CC0).
        </p>
      </main>

      {teamId && (
        <>
          <div className="panel-backdrop" onClick={closeTeam} aria-hidden="true" />
          <TeamDetail key={teamId} teamId={teamId} onClose={closeTeam} />
        </>
      )}
    </div>
  );
}
