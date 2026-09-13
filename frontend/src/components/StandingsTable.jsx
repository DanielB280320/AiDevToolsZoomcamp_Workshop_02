import { formatGoalDifference } from '../lib/format.js';
import { Crest } from './Crest.jsx';

// Shows the short label but gives screen readers the full column name.
function ColumnHeader({ short, full, className }) {
  return (
    <th scope="col" className={className} title={full}>
      <span aria-hidden="true">{short}</span>
      <span className="visually-hidden">{full}</span>
    </th>
  );
}

export function StandingsTable({ league, teams, selectedTeamId, onSelectTeam }) {
  return (
    <div className="table-card">
      <table className="standings">
        <caption className="visually-hidden">{league.name} standings</caption>
        <thead>
          <tr>
            <ColumnHeader short="#" full="Position" className="standings__pos" />
            <th scope="col" className="standings__team">Team</th>
            <ColumnHeader short="P" full="Played" />
            <ColumnHeader short="W" full="Wins" className="hide-narrow" />
            <ColumnHeader short="D" full="Draws" className="hide-narrow" />
            <ColumnHeader short="L" full="Losses" className="hide-narrow" />
            <ColumnHeader short="GD" full="Goal difference" />
            <ColumnHeader short="Pts" full="Points" />
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr
              key={team.id}
              className={team.id === selectedTeamId ? 'is-selected' : undefined}
              style={{ '--team': team.crest.color }}
              onClick={() => onSelectTeam(team.id)}
            >
              <td className="standings__pos">
                <span className="pos-chip" data-rank={team.position <= 3 ? team.position : undefined}>
                  {team.position}
                </span>
              </td>
              <th scope="row" className="standings__team">
                {/* The whole row is clickable; the button makes it reachable by keyboard. Its click bubbles to the row. */}
                <button type="button" className="team-link" aria-pressed={team.id === selectedTeamId}>
                  <Crest crest={team.crest} />
                  {team.name}
                </button>
              </th>
              <td>{team.played}</td>
              <td className="hide-narrow">{team.wins}</td>
              <td className="hide-narrow">{team.draws}</td>
              <td className="hide-narrow">{team.losses}</td>
              <td className={team.goalDifference > 0 ? 'gd gd--up' : team.goalDifference < 0 ? 'gd gd--down' : 'gd'}>
                {formatGoalDifference(team.goalDifference)}
              </td>
              <td className="standings__pts">
                <span className="pts-chip">{team.points}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
