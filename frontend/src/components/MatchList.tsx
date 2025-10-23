import React from 'react';
import type { Match } from '../types';

interface Props {
  matches: Match[];
}

export const MatchList: React.FC<Props> = ({ matches }) => {
  if (!matches.length) {
    return <p>Select a guideline to view candidate matches.</p>;
  }

  return (
    <section>
      <h2>Candidate Matches</h2>
      {matches.map((match) => (
        <article className="match-card" key={match.id}>
          <header>
            <div className="match-card__status">
              <span>{match.status.toUpperCase()}</span>
              <span>{Math.round(match.confidence * 100)}% confidence</span>
            </div>
          </header>
          <p>{match.rationale}</p>
          <footer>
            <small>Regulation #{match.regulationId}</small>
          </footer>
        </article>
      ))}
    </section>
  );
};
