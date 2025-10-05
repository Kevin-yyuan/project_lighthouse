import React from 'react';

const RiskBadge = ({ risk }) => {
  if (!risk) return null;
  const riskColorMap = {
    High: 'danger',
    Medium: 'warning',
    Low: 'success',
  };
  const badgeClass = `badge bg-${riskColorMap[risk]}`;
  return <span className={badgeClass}>{risk}</span>;
};

const SortableHeader = ({ children, name, sortConfig, requestSort }) => {
  const getSortIcon = () => {
    if (sortConfig.key !== name) return null;
    if (sortConfig.direction === 'ascending') return ' ▲';
    return ' ▼';
  };

  return (
    <th scope="col" onClick={() => requestSort(name)} style={{ cursor: 'pointer' }}>
      {children}
      {getSortIcon()}
    </th>
  );
};

const ProjectTable = ({ projects, requestSort, sortConfig, onRowClick }) => {

  const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);
  };

  return (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="thead-dark">
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Property</th>
            <th scope="col">City</th>
            <th scope="col">Type</th>
            <th scope="col">Contractor</th>
            <th scope="col">Status</th>
            <SortableHeader name="Budget" sortConfig={sortConfig} requestSort={requestSort}>
              Budget
            </SortableHeader>
            <SortableHeader name="PredictedCost" sortConfig={sortConfig} requestSort={requestSort}>
              Predicted Cost
            </SortableHeader>
            <SortableHeader name="PredictedDuration_Days" sortConfig={sortConfig} requestSort={requestSort}>
              Predicted Duration
            </SortableHeader>
            <SortableHeader name="RiskScore" sortConfig={sortConfig} requestSort={requestSort}>
              Risk Score
            </SortableHeader>
            <th scope="col">Primary Risk Factor</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.ProjectID} onClick={() => onRowClick(p)} style={{ cursor: 'pointer' }}>
              <td>{p.ProjectID}</td>
              <td>{p.PropertyName}</td>
              <td>{p.City}</td>
              <td>{p.ProjectType}</td>
              <td>
                <span className="badge bg-secondary">{p.Vendor}</span>
              </td>
              <td>{p.ProjectStatus}</td>
              <td>{formatCurrency(p.Budget)}</td>
              <td>
                {p.PredictedCost ? (
                  <span className={p.PredictedCost <= p.Budget ? 'text-success' : 'text-danger'}>
                    {formatCurrency(p.PredictedCost)}
                    {p.Budget ? (
                      <span className="small">
                        {' '}({((p.PredictedCost - p.Budget) / p.Budget * 100).toFixed(1)}%)
                      </span>
                    ) : null}
                  </span>
                ) : (
                  <span className="text-muted">N/A</span>
                )}
              </td>
              <td>
                {p.PredictedDuration_Days ? (
                  <span className={(() => {
                    if (!p.StartDate || !p.PlannedEndDate) return 'text-primary';
                    const startDate = new Date(p.StartDate);
                    const plannedEndDate = new Date(p.PlannedEndDate);
                    const plannedDuration = Math.ceil((plannedEndDate - startDate) / (1000 * 60 * 60 * 24));
                    return p.PredictedDuration_Days <= plannedDuration ? 'text-success' : 'text-danger';
                  })()}>
                    {p.PredictedDuration_Days} days
                    {(() => {
                      if (!p.StartDate || !p.PlannedEndDate) return null;
                      const startDate = new Date(p.StartDate);
                      const plannedEndDate = new Date(p.PlannedEndDate);
                      const plannedDuration = Math.ceil((plannedEndDate - startDate) / (1000 * 60 * 60 * 24));
                      const daysDifference = p.PredictedDuration_Days - plannedDuration;
                      const sign = daysDifference > 0 ? '+' : '';
                      return <span className="small"> ({sign}{daysDifference} days)</span>;
                    })()}
                  </span>
                ) : (
                  <span className="text-muted">N/A</span>
                )}
              </td>
              <td>
                <RiskBadge risk={p.PredictedRisk} />
                <span className="ms-2">{p.RiskScore !== null ? (p.RiskScore * 100).toFixed(1) + '%' : ''}</span>
              </td>
              <td>{p.PrimaryRiskFactor || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProjectTable;
