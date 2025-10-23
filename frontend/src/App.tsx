import React from 'react';
import { useGuidelines } from './hooks/useGuidelines';
import { useMatches } from './hooks/useMatches';
import { FilterPanel } from './components/FilterPanel';
import { MatchList } from './components/MatchList';
import { UploadPanel } from './components/UploadPanel';
import { GuidelineViewer } from './components/GuidelineViewer';
import { MatchDetailPanel } from './components/MatchDetailPanel';

const App: React.FC = () => {
  const [selectedGuideline, setSelectedGuideline] = React.useState<string | null>(null);
  const [activeMatchId, setActiveMatchId] = React.useState<number | null>(null);
  const [filters, setFilters] = React.useState({
    language: 'en',
    region: 'global',
    regulationType: 'all',
  });

  const { data: guidelines } = useGuidelines(filters.language);
  const { data: matches } = useMatches(selectedGuideline);
  const selectedGuidelineObject = React.useMemo(
    () => guidelines?.find((item) => item.id.toString() === selectedGuideline) ?? null,
    [guidelines, selectedGuideline],
  );
  const activeMatch = React.useMemo(
    () => matches?.find((match) => match.id === activeMatchId) ?? null,
    [matches, activeMatchId],
  );

  React.useEffect(() => {
    setActiveMatchId(null);
  }, [selectedGuideline]);

  return (
    <div className="app">
      <header className="app__header">
        <h1>EchoGraph</h1>
        <p>Explore cloud guidelines and validate regulation matches.</p>
      </header>
      <div className="app__content">
        <aside className="app__sidebar">
          <UploadPanel />
          <FilterPanel filters={filters} onChange={setFilters} />
          <ul className="guideline-list">
            {guidelines?.map((guideline) => {
              const isActive = selectedGuideline === guideline.id.toString();
              return (
                <li key={guideline.id}>
                  <button
                    type="button"
                    className={isActive ? 'is-active' : ''}
                    onClick={() => setSelectedGuideline(guideline.id.toString())}
                  >
                    <strong>{guideline.title}</strong>
                    <span>{guideline.language.toUpperCase()}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>
        <main className="app__main">
          <GuidelineViewer
            guideline={selectedGuidelineObject}
            matches={matches ?? []}
            activeMatchId={activeMatchId}
            onActivate={setActiveMatchId}
          />
        </main>
        <aside className="app__aside">
          <MatchList matches={matches ?? []} activeMatchId={activeMatchId} onActivate={setActiveMatchId} />
          <MatchDetailPanel match={activeMatch ?? null} />
        </aside>
      </div>
    </div>
  );
};

export default App;
