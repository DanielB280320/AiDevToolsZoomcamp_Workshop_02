import { LeagueLogo } from './LeagueLogo.jsx';
import { StatusMessage } from './StatusMessage.jsx';

const REGION_ORDER = ['Europe', 'Americas', 'Continental'];

export function Sidebar({ leagues, status, error, onRetry, selectedLeagueId, onSelect }) {
  const groups = REGION_ORDER.map((region) => ({
    region,
    leagues: leagues.filter((league) => league.region === region),
  })).filter((group) => group.leagues.length > 0);

  return (
    <div className="sidebar">
      <div className="brand">
        <img className="brand__logo" src="/kickboard-logo.svg" alt="" width="36" height="36" />
        Kickboard
      </div>
      <nav aria-label="Leagues">
        {status === 'loading' && <StatusMessage>Loading leagues…</StatusMessage>}
        {status === 'error' && <StatusMessage error={error} onRetry={onRetry} />}
        <div className="league-groups">
          {groups.map((group) => (
            <section key={group.region} className="league-group">
              <h2 className="league-group__title">{group.region}</h2>
              <ul>
                {group.leagues.map((league) => (
                  <li key={league.id}>
                    <button
                      type="button"
                      className="league-link"
                      style={{ '--chip': league.color }}
                      aria-current={league.id === selectedLeagueId ? 'page' : undefined}
                      onClick={() => onSelect(league.id)}
                    >
                      <LeagueLogo league={league} />
                      {league.name}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </nav>
    </div>
  );
}
