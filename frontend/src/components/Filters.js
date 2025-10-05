import React from 'react';

const Filters = ({ filters, onFilterChange }) => {

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    onFilterChange(name, value);
  };

  const handleReset = () => {
    onFilterChange('ProjectStatus', '');
    onFilterChange('PredictedRisk', '');
    onFilterChange('City', '');
  };

  // Hardcoded options for simplicity
  const statusOptions = ["Completed", "In Progress", "Not Started"];
  const riskOptions = ["High", "Medium", "Low"];
  const cityOptions = ["Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa", "Halifax"];

  return (
    <div className="row mb-3 align-items-end">
      <div className="col-md-3">
        <label htmlFor="statusFilter" className="form-label">Status</label>
        <select 
          id="statusFilter" 
          className="form-select" 
          name="ProjectStatus"
          value={filters.ProjectStatus || ''}
          onChange={handleInputChange}
        >
          <option value="">All</option>
          {statusOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
        </select>
      </div>
      <div className="col-md-3">
        <label htmlFor="riskFilter" className="form-label">Risk</label>
        <select 
          id="riskFilter" 
          className="form-select" 
          name="PredictedRisk"
          value={filters.PredictedRisk || ''}
          onChange={handleInputChange}
        >
          <option value="">All</option>
          {riskOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
        </select>
      </div>
      <div className="col-md-3">
        <label htmlFor="cityFilter" className="form-label">City</label>
        <select 
          id="cityFilter" 
          className="form-select" 
          name="City"
          value={filters.City || ''}
          onChange={handleInputChange}
        >
          <option value="">All</option>
          {cityOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
        </select>
      </div>
      <div className="col-md-3 d-flex align-items-end">
        <button className="btn btn-secondary" onClick={handleReset}>Reset Filters</button>
      </div>
    </div>
  );
};

export default Filters;
