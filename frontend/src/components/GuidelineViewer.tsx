import React from 'react';
import type { Guideline, Match } from '../types';

type Props = {
  guideline: Guideline | null;
  matches: Match[];
  activeMatchId: number | null;
  onActivate: (matchId: number | null) => void;
};

type Segment = {
  text: string;
  matches: Match[];
};

export const GuidelineViewer: React.FC<Props> = ({ guideline, matches, activeMatchId, onActivate }) => {
  if (!guideline) {
    return (
      <section className="guideline-viewer">
        <h2>Guideline</h2>
        <p>Select a guideline section to review matches.</p>
      </section>
    );
  }

  const segments = React.useMemo(() => buildSegments(guideline.body, matches), [guideline.body, matches]);

  return (
    <section className="guideline-viewer">
      <h2>{guideline.title}</h2>
      <div className="guideline-viewer__body">
        {segments.map((segment, index) => {
          if (!segment.matches.length) {
            return <span key={`segment-${index}`}>{segment.text}</span>;
          }

          const isActive = segment.matches.some((match) => match.id === activeMatchId);
          const primaryMatch = segment.matches[0];
          const tooltip = segment.matches
            .map((match) => {
              const regulationTitle = match.regulationSection?.title ?? `Regulation #${match.regulationId}`;
              return `${regulationTitle} (${Math.round(match.confidence * 100)}%)`;
            })
            .join('\n');

          return (
            <span
              key={`segment-${index}`}
              className={`guideline-viewer__highlight${isActive ? ' is-active' : ''}`}
              onMouseEnter={() => onActivate(primaryMatch.id)}
              onFocus={() => onActivate(primaryMatch.id)}
              onClick={() => onActivate(primaryMatch.id)}
              tabIndex={0}
              title={tooltip}
            >
              {segment.text}
            </span>
          );
        })}
      </div>
    </section>
  );
};

const buildSegments = (body: string, matches: Match[]): Segment[] => {
  if (!body) {
    return [];
  }

  const rangeMap = new Map<string, { start: number; end: number; matches: Match[] }>();

  matches.forEach((match) => {
    let start = match.guidelineSpan?.start ?? null;
    let end = match.guidelineSpan?.end ?? null;

    if (start === null || end === null || end <= start || end > body.length) {
      if (match.guidelineExcerpt) {
        const located = body.indexOf(match.guidelineExcerpt);
        if (located !== -1) {
          start = located;
          end = located + match.guidelineExcerpt.length;
        }
      }
    }

    if (start === null || end === null || end <= start) {
      return;
    }

    const safeStart = Math.max(0, Math.min(body.length, start));
    const safeEnd = Math.max(safeStart, Math.min(body.length, end));
    if (safeEnd <= safeStart) {
      return;
    }
    const key = `${safeStart}:${safeEnd}`;
    const existing = rangeMap.get(key);
    if (existing) {
      existing.matches.push(match);
    } else {
      rangeMap.set(key, { start: safeStart, end: safeEnd, matches: [match] });
    }
  });

  const ranges = Array.from(rangeMap.values()).sort((a, b) => a.start - b.start);
  const segments: Segment[] = [];
  let cursor = 0;

  ranges.forEach((range) => {
    if (range.start > cursor) {
      segments.push({ text: body.slice(cursor, range.start), matches: [] });
    }
    const highlightedText = body.slice(range.start, range.end);
    if (highlightedText) {
      segments.push({ text: highlightedText, matches: range.matches });
    }
    cursor = Math.max(cursor, range.end);
  });

  if (cursor < body.length) {
    segments.push({ text: body.slice(cursor), matches: [] });
  }

  return segments;
};
