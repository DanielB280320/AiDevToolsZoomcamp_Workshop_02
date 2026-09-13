import { useEffect, useId, useRef } from 'react';
import { getTeamDetail } from '../api/kickboardApi.js';
import { useAsync } from '../hooks/useAsync.js';
import { readableTextColor } from '../lib/color.js';
import { formatMatchDate, ordinal, plural } from '../lib/format.js';
import {
  COMPOSITE_WEIGHTS,
  bestPlayerInMatch,
  groupSquadByPosition,
  resultFor,
  topScorer,
} from '../lib/teamStats.js';
import { Crest } from './Crest.jsx';
import { LeagueLogo } from './LeagueLogo.jsx';
import { StatusMessage } from './StatusMessage.jsx';

const OUTCOME_LABELS = { W: 'Win', D: 'Draw', L: 'Loss' };

export function TeamDetail({ teamId, onClose }) {
  const detail = useAsync(() => getTeamDetail(teamId), [teamId]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  return (
    <aside className="team-panel" aria-label="Team details">
      <div className="team-panel__toolbar">
        <span className="team-panel__eyebrow">Team details</span>
        <button type="button" className="icon-button" onClick={onClose} aria-label="Close team details">
          ✕
        </button>
      </div>
      {detail.status === 'loading' && <StatusMessage>Loading team…</StatusMessage>}
      {detail.status === 'error' && <StatusMessage error={detail.error} onRetry={detail.retry} />}
      {detail.status === 'success' && <TeamDetailContent detail={detail.data} />}
    </aside>
  );
}

function TeamDetailContent({ detail }) {
  const { team, league, squad, recentMatches } = detail;
  const headingRef = useRef(null);
  const scorerId = useId();
  const bestId = useId();
  const resultsId = useId();
  const squadId = useId();

  useEffect(() => {
    headingRef.current?.focus();
  }, [team.id]);

  const scorer = topScorer(squad);
  const lastMatch = recentMatches[0] ?? null;
  const best = lastMatch ? bestPlayerInMatch(lastMatch, squad) : null;
  const lastResult = lastMatch ? resultFor(lastMatch, team.id) : null;

  return (
    <div
      className="team-detail"
      style={{ '--team-accent': team.crest.color, '--team-fg': readableTextColor(team.crest.color) }}
    >
      <header className="team-header">
        <span className="team-header__crest">
          <Crest crest={team.crest} size="lg" />
        </span>
        <div>
          <h2 className="team-header__name" ref={headingRef} tabIndex={-1}>
            {team.name}
          </h2>
          <p className="team-header__meta">
            <LeagueLogo league={league} size="xs" />
            <span className="team-header__meta-text">
              {league.name} · {ordinal(team.position)} · {plural(team.points, 'pt')}
            </span>
          </p>
        </div>
      </header>

      <div className="highlights">
        <section className="highlight highlight--scorer" aria-labelledby={scorerId}>
          <h3 id={scorerId} className="highlight__label">
            <span className="highlight__icon" aria-hidden="true">⚽</span>
            Top scorer
          </h3>
          {scorer ? (
            <>
              <p className="highlight__value">{scorer.name}</p>
              <p className="highlight__meta">
                {plural(scorer.goals, 'goal')} · {plural(scorer.assists, 'assist')}
              </p>
            </>
          ) : (
            <p className="highlight__meta">No goals scored yet</p>
          )}
        </section>

        <section className="highlight highlight--best" aria-labelledby={bestId}>
          <h3 id={bestId} className="highlight__label">
            <span className="highlight__icon" aria-hidden="true">★</span>
            Best player in last match
          </h3>
          {best ? (
            <>
              <p className="highlight__value">{best.player.name}</p>
              <p className="highlight__meta">
                {lastResult.isHome ? 'vs' : 'at'} {lastResult.opponent.name} · {lastResult.goalsFor}–{lastResult.goalsAgainst}
              </p>
              <dl className="breakdown">
                <div><dt>Goals</dt><dd>{best.stats.goals}</dd></div>
                <div><dt>Assists</dt><dd>{best.stats.assists}</dd></div>
                <div><dt>Rating</dt><dd>{best.stats.rating.toFixed(1)}</dd></div>
                <div><dt>Mins</dt><dd>{best.stats.minutesPlayed}</dd></div>
                <div><dt>Score</dt><dd>{best.score.toFixed(1)}</dd></div>
              </dl>
              <details className="formula">
                <summary>How is this calculated?</summary>
                <p>
                  Goals × {COMPOSITE_WEIGHTS.goals} + assists × {COMPOSITE_WEIGHTS.assists} + rating ×{' '}
                  {COMPOSITE_WEIGHTS.rating} + minutes ÷ 90 × {COMPOSITE_WEIGHTS.per90Minutes}
                </p>
              </details>
            </>
          ) : (
            <p className="highlight__meta">No matches played yet</p>
          )}
        </section>
      </div>

      <section className="detail-section" aria-labelledby={resultsId}>
        <h3 id={resultsId} className="detail-section__title">Recent results</h3>
        {recentMatches.length === 0 ? (
          <p className="muted">No matches played yet</p>
        ) : (
          <ol className="results" aria-labelledby={resultsId}>
            {recentMatches.map((match) => {
              const result = resultFor(match, team.id);
              return (
                <li key={match.id} className="result">
                  <span className={`result__badge result__badge--${result.outcome}`}>
                    <span aria-hidden="true">{result.outcome}</span>
                    <span className="visually-hidden">{OUTCOME_LABELS[result.outcome]}</span>
                  </span>
                  <span className="result__opponent">
                    <span className="result__venue">{result.isHome ? 'vs' : 'at'}</span>
                    <Crest crest={result.opponent.crest} size="sm" />
                    <span className="result__opponent-name">{result.opponent.name}</span>
                  </span>
                  <span className="result__score">
                    {result.goalsFor}–{result.goalsAgainst}
                  </span>
                  <time className="result__date" dateTime={match.date}>
                    {formatMatchDate(match.date)}
                  </time>
                </li>
              );
            })}
          </ol>
        )}
      </section>

      <section className="detail-section" aria-labelledby={squadId}>
        <h3 id={squadId} className="detail-section__title">
          Squad <span className="muted">({squad.length})</span>
        </h3>
        {groupSquadByPosition(squad).map((group) => (
          <div key={group.key} className="squad-group" data-position={group.key}>
            <h4 className="squad-group__title">{group.label}</h4>
            <ul className="squad-list" aria-label={group.label}>
              {group.players.map((player) => (
                <li key={player.id} className={player.id === scorer?.id ? 'is-top-scorer' : undefined}>
                  <span className="squad-list__number">{player.shirtNumber}</span>
                  <span className="squad-list__name">{player.name}</span>
                  <span className="squad-list__stats">
                    {player.goals} <abbr title="goals">G</abbr> · {player.assists} <abbr title="assists">A</abbr>
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </div>
  );
}
