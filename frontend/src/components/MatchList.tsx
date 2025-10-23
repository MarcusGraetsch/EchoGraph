import React from 'react';
import type { Match } from '../types';

interface Props {
  matches: Match[];
  activeMatchId: number | null;
  onActivate: (matchId: number | null) => void;
}

export const MatchList: React.FC<Props> = ({ matches, activeMatchId, onActivate }) => {
  if (!matches.length) {
    return <p>Select a guideline to view candidate matches.</p>;
  }

  return (
    <section className="match-list">
      <h2>Candidate matches</h2>
      <ul>
        {matches.map((match) => {
          const isActive = match.id === activeMatchId;
          const regulationTitle = match.regulationSection?.title ?? `Regulation #${match.regulationId}`;
          return (
            <li
              key={match.id}
              className={`match-card${isActive ? ' is-active' : ''}`}
              onMouseEnter={() => onActivate(match.id)}
              onFocus={() => onActivate(match.id)}
              onClick={() => onActivate(match.id)}
              tabIndex={0}
            >
              <header>
                <div className="match-card__status">
                  <span>{match.status.toUpperCase()}</span>
                  <span>{Math.round(match.confidence * 100)}% confidence</span>
                </div>
                <h3>{regulationTitle}</h3>
              </header>
              <p className="match-card__rationale">{match.rationale}</p>
              {match.regulationExcerpt && (
                <blockquote className="match-card__excerpt">{match.regulationExcerpt}</blockquote>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
};
