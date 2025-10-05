import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

// --- Re-introducing KPI Card Component ---
const KpiCard = ({ title, value, icon, color }) => {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <div className="d-flex align-items-center">
          <div className={`fs-2 me-3 text-${color}`}>{icon}</div>
          <div>
            <h6 className="card-subtitle text-muted">{title}</h6>
            <h4 className="card-title mb-0">{value}</h4>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Chart Components (no change) ---
const RiskDistributionChart = ({ data }) => {
  const options = { responsive: true, plugins: { legend: { position: 'top' }, title: { display: true, text: 'Project Risk Distribution' } } };
  return <Doughnut data={data} options={options} />;
};

const ProjectsByCityChart = ({ data }) => {
  const options = { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: 'Projects by City' } }, scales: { y: { beginAtZero: true } } };
  return <Bar data={data} options={options} />;
};


const Dashboard = ({ projects }) => {
  // --- Process Data for KPIs and Charts ---
  const totalProjects = projects.length;
  const highRiskProjects = projects.filter(p => p.PredictedRisk === 'High').length;
  const totalBudget = projects.reduce((acc, p) => acc + (p.Budget || 0), 0);
  const totalBudgetVariance = projects.filter(p => p.ProjectStatus === 'Completed' && p.BudgetVariance_CAD).reduce((acc, p) => acc + p.BudgetVariance_CAD, 0);

  const formatCurrency = (num) => {
    if (Math.abs(num) >= 1_000_000) return `$${(num / 1_000_000).toFixed(2)}M`;
    if (Math.abs(num) >= 1_000) return `$${(num / 1_000).toFixed(1)}K`;
    return `$${num}`;
  };

  const riskCounts = projects.reduce((acc, p) => {
    const risk = p.PredictedRisk || 'N/A';
    acc[risk] = (acc[risk] || 0) + 1;
    return acc;
  }, {});

  const riskChartData = {
    labels: Object.keys(riskCounts),
    datasets: [{
      label: '# of Projects',
      data: Object.values(riskCounts),
      backgroundColor: ['rgba(255, 99, 132, 0.5)', 'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)', 'rgba(153, 102, 255, 0.5)'],
      borderColor: ['rgba(255, 99, 132, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
      borderWidth: 1,
    }],
  };

  const cityCounts = projects.reduce((acc, p) => {
    acc[p.City] = (acc[p.City] || 0) + 1;
    return acc;
  }, {});

  const cityChartData = {
    labels: Object.keys(cityCounts),
    datasets: [{
      label: '# of Projects',
      data: Object.values(cityCounts),
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
    }],
  };

  return (
    <div className="row">
      {/* --- Left Column: KPIs --- */}
      <div className="col-lg-3">
        <h5 className="mb-3">Portfolio Snapshot</h5>
        <KpiCard title="Total Projects" value={totalProjects} icon="📊" color="primary" />
        <KpiCard title="High Risk Projects" value={highRiskProjects} icon="⚠️" color="warning" />
        <KpiCard title="Total Budget" value={formatCurrency(totalBudget)} icon="💰" color="info" />
        <KpiCard title="Budget Variance" value={formatCurrency(totalBudgetVariance)} icon="📈" color={totalBudgetVariance > 0 ? 'danger' : 'success'} />
      </div>

      {/* --- Right Column: Charts --- */}
      <div className="col-lg-9">
        <div className="card mb-4">
            <div className="card-body">
                <ProjectsByCityChart data={cityChartData} />
            </div>
        </div>
        <div className="row">
            <div className="col-lg-7">
                <div className="card">
                    <div className="card-body">
                        <RiskDistributionChart data={riskChartData} />
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
