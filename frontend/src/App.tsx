import React from 'react';
import { useGuidelines } from './hooks/useGuidelines';
import { useMatches } from './hooks/useMatches';
import { FilterPanel } from './components/FilterPanel';
import { MatchList } from './components/MatchList';

const App: React.FC = () => {
  const [selectedGuideline, setSelectedGuideline] = React.useState<string | null>(null);
  const [filters, setFilters] = React.useState({
    language: 'en',
    region: 'global',
    regulationType: 'all',
  });

  const { data: guidelines } = useGuidelines(filters.language);
  const { data: matches } = useMatches(selectedGuideline);

  return (
    <div className="app">
      <header className="app__header">
        <h1>EchoGraph</h1>
        <p>Explore cloud guidelines and validate regulation matches.</p>
      </header>
      <div className="app__content">
        <aside className="app__sidebar">
          <FilterPanel filters={filters} onChange={setFilters} />
          <ul className="guideline-list">
            {guidelines?.map((guideline) => (
              <li key={guideline.id}>
                <button type="button" onClick={() => setSelectedGuideline(guideline.id.toString())}>
                  <strong>{guideline.title}</strong>
                  <span>{guideline.language.toUpperCase()}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>
        <main className="app__main">
          <MatchList matches={matches ?? []} />
        </main>
      </div>
    </div>
  );
};

export default App;
