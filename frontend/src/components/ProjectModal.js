import React from 'react';
import './ProjectModal.css';

const DetailItem = ({ label, value, isCurrency = false }) => {
  const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);
  };

  return (
    <div className="col-md-6 mb-3">
      <strong>{label}:</strong>
      <p className="text-muted">{isCurrency ? formatCurrency(value) : (value || 'N/A')}</p>
    </div>
  );
};

const ProjectModal = ({ project, onClose }) => {
  if (!project) return null;

  return (
    <>
      <div className="modal-backdrop"></div>
      <div className="modal show d-block" tabIndex="-1">
        <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">{project.ProjectID}: {project.PropertyName}</h5>
              <button type="button" className="btn-close" onClick={onClose}></button>
            </div>
            <div className="modal-body">
              <div className="row">
                <DetailItem label="Status" value={project.ProjectStatus} />
                <DetailItem label="Project Type" value={project.ProjectType} />
                <DetailItem label="City" value={project.City} />
                <DetailItem label="Contractor" value={<span className="badge bg-secondary fs-6">{project.Vendor}</span>} />
                <hr className="my-3" />
                <DetailItem label="Start Date" value={project.StartDate ? new Date(project.StartDate).toLocaleDateString() : 'N/A'} />
                <DetailItem label="Planned End Date" value={project.PlannedEndDate ? new Date(project.PlannedEndDate).toLocaleDateString() : 'N/A'} />
                <DetailItem label="Actual End Date" value={project.ActualEndDate ? new Date(project.ActualEndDate).toLocaleDateString() : 'N/A'} />
                <DetailItem label="Schedule Variance" value={`${project.ScheduleVariance_Days || 0} days`} />
                <hr className="my-3" />
                <DetailItem label="Budget" value={project.Budget} isCurrency />
                <DetailItem label="Actual Cost" value={project.ActualCost} isCurrency />
                <DetailItem label="Budget Variance" value={project.BudgetVariance_CAD} isCurrency />
                <div className="col-md-6 mb-3">
                  <strong>Predicted Cost:</strong>
                  <p className={project.PredictedCost && project.Budget ? 
                    (project.PredictedCost <= project.Budget ? 'text-success' : 'text-danger') : 'text-muted'}>
                    {project.PredictedCost ? 
                      new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(project.PredictedCost) 
                      : 'N/A'}
                    {project.PredictedCost && project.Budget ? (
                      <span className="small">
                        {' '}({((project.PredictedCost - project.Budget) / project.Budget * 100).toFixed(1)}%)
                      </span>
                    ) : null}
                  </p>
                </div>
                <hr className="my-3" />
                <div className="col-md-6 mb-3">
                  <strong>Predicted Duration:</strong>
                  <p className={(() => {
                    if (!project.PredictedDuration_Days) return 'text-muted';
                    if (!project.StartDate || !project.PlannedEndDate) return 'text-primary';
                    const startDate = new Date(project.StartDate);
                    const plannedEndDate = new Date(project.PlannedEndDate);
                    const plannedDuration = Math.ceil((plannedEndDate - startDate) / (1000 * 60 * 60 * 24));
                    return project.PredictedDuration_Days <= plannedDuration ? 'text-success' : 'text-danger';
                  })()}>
                    {project.PredictedDuration_Days ? `${project.PredictedDuration_Days} days` : 'N/A'}
                    {(() => {
                      if (!project.PredictedDuration_Days || !project.StartDate || !project.PlannedEndDate) return null;
                      const startDate = new Date(project.StartDate);
                      const plannedEndDate = new Date(project.PlannedEndDate);
                      const plannedDuration = Math.ceil((plannedEndDate - startDate) / (1000 * 60 * 60 * 24));
                      const daysDifference = project.PredictedDuration_Days - plannedDuration;
                      const sign = daysDifference > 0 ? '+' : '';
                      return <span className="small"> ({sign}{daysDifference} days)</span>;
                    })()}
                  </p>
                </div>
                <hr className="my-3" />
                <DetailItem label="Predicted Risk" value={project.PredictedRisk} />
                <DetailItem label="Risk Score" value={project.RiskScore ? (project.RiskScore * 100).toFixed(1) + '%' : 'N/A'} />
                <DetailItem label="Primary Risk Factor" value={project.PrimaryRiskFactor} />
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Close</button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProjectModal;
