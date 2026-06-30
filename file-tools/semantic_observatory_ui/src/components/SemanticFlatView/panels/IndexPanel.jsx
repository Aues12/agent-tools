export function IndexPanel({
  designMode,
  designModes,
  filterOptions,
  filters,
  query,
  sortMode,
  sortOptions,
  onDesignModeChange,
  onFileAnalyze,
  onFilterChange,
  onQueryChange,
  onSortModeChange,
  sourceName,
  status,
}) {
  return (
    <aside className="index-panel flat-panel" aria-label="Tools and filters">
      <div className="panel-header">
        <p className="eyebrow">Semantic Observatory</p>
        <h1>Flat View</h1>
      </div>

      <div className="design-switcher" aria-label="Visual language">
        {designModes.map((mode) => (
          <button
            key={mode.id}
            type="button"
            className={
              designMode === mode.id
                ? "design-switcher__button design-switcher__button--active"
                : "design-switcher__button"
            }
            onClick={() => onDesignModeChange(mode.id)}
          >
            {mode.label}
          </button>
        ))}
      </div>

      <label className="upload-field">
        <span>Analyze .py</span>
        <input
          type="file"
          accept=".py,text/x-python,text/plain"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              onFileAnalyze(file);
            }
            event.target.value = "";
          }}
        />
      </label>

      <div className={`analysis-status analysis-status--${status.state}`}>
        <span>{sourceName}</span>
        <strong>{status.message}</strong>
      </div>

      <label className="search-field">
        <span>Search</span>
        <input
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="parse, builder, dfg"
        />
      </label>

      <label className="select-field sort-field">
        <span>Sort</span>
        <select
          value={sortMode}
          onChange={(event) => onSortModeChange(event.target.value)}
        >
          {sortOptions.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <div className="filter-stack" aria-label="Filters">
        {Object.entries(filterOptions).map(([key, values]) => (
          <label key={key} className="select-field">
            <span>{key}</span>
            <select
              value={filters[key]}
              onChange={(event) => onFilterChange(key, event.target.value)}
            >
              {values.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
    </aside>
  );
}
