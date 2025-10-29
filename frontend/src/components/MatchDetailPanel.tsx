import React from 'react';
import type { Match } from '../types';

interface Props {
  match: Match | null;
}

export const MatchDetailPanel: React.FC<Props> = ({ match }) => {
  if (!match) {
    return (
      <section className="match-detail">
        <h2>Match details</h2>
        <p>Hover over a highlighted section or match card to inspect details.</p>
      </section>
    );
  }

  const regulationTitle = match.regulationSection?.title ?? `Regulation #${match.regulationId}`;

  return (
    <section className="match-detail">
      <h2>Match details</h2>
      <header className="match-detail__header">
        <h3>{regulationTitle}</h3>
        <span>{Math.round(match.confidence * 100)}% confidence</span>
      </header>
      <p className="match-detail__rationale">{match.rationale}</p>
      <div className="match-detail__excerpt">
        <h4>Regulation excerpt</h4>
        <p>{match.regulationExcerpt ?? 'No excerpt available.'}</p>
      </div>
      <div className="match-detail__excerpt">
        <h4>Guideline excerpt</h4>
        <p>{match.guidelineExcerpt ?? 'No excerpt available.'}</p>
      </div>
    </section>
  );
};
