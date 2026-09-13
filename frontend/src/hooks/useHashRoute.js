import { useCallback, useEffect, useState } from 'react';

// Routes: #/leagues/:leagueId and #/leagues/:leagueId/teams/:teamId

export function parseHash(hash) {
  const [section, leagueId, subsection, teamId] = hash
    .replace(/^#\/?/, '')
    .split('/')
    .map(decodeURIComponent);

  return {
    leagueId: section === 'leagues' && leagueId ? leagueId : null,
    teamId: section === 'leagues' && subsection === 'teams' && teamId ? teamId : null,
  };
}

export function buildHash({ leagueId, teamId }) {
  if (!leagueId) return '#/';
  const leaguePath = `#/leagues/${encodeURIComponent(leagueId)}`;
  return teamId ? `${leaguePath}/teams/${encodeURIComponent(teamId)}` : leaguePath;
}

/** Keeps the selected league/team in the URL so views are shareable and Back works. */
export function useHashRoute() {
  const [route, setRoute] = useState(() => parseHash(window.location.hash));

  useEffect(() => {
    const sync = () => setRoute(parseHash(window.location.hash));
    window.addEventListener('hashchange', sync);
    window.addEventListener('popstate', sync);
    return () => {
      window.removeEventListener('hashchange', sync);
      window.removeEventListener('popstate', sync);
    };
  }, []);

  const navigate = useCallback((next) => {
    const hash = buildHash(next);
    if (hash !== window.location.hash) window.history.pushState(null, '', hash);
    setRoute(parseHash(hash));
  }, []);

  return [route, navigate];
}
