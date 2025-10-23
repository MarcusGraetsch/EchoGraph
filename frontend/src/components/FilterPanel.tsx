import React from 'react';

type Filters = {
  language: string;
  region: string;
  regulationType: string;
};

type Props = {
  filters: Filters;
  onChange: (filters: Filters) => void;
};

export const FilterPanel: React.FC<Props> = ({ filters, onChange }) => {
  const update = (key: keyof Filters) => (event: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({ ...filters, [key]: event.target.value });
  };

  return (
    <section>
      <h2>Filters</h2>
      <label>
        Language
        <select value={filters.language} onChange={update('language')}>
          <option value="en">English</option>
          <option value="es">Spanish</option>
        </select>
      </label>
      <label>
        Region
        <select value={filters.region} onChange={update('region')}>
          <option value="global">Global</option>
          <option value="us">United States</option>
          <option value="eu">European Union</option>
        </select>
      </label>
      <label>
        Regulation Type
        <select value={filters.regulationType} onChange={update('regulationType')}>
          <option value="all">All</option>
          <option value="privacy">Privacy</option>
          <option value="security">Security</option>
        </select>
      </label>
    </section>
  );
};
