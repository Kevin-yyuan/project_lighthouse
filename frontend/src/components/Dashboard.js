import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
} from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title);

// --- Re-introducing KPI Card Component ---
const KpiCard = ({ title, value, icon, color }) => {
  return (
    <div className={`card mb-3 border-${color}`}>
      <div className="card-body">
        <div className="d-flex align-items-center">
          <div className={`fs-2 me-3 text-${color}`}>{icon}</div>
          <div>
            <h6 className="card-subtitle text-muted">{title}</h6>
            <h4 className={`card-title mb-0 text-${color}`}>{value}</h4>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Chart Components (no change) ---
const RiskDistributionChart = ({ data }) => {
  const options = { 
    responsive: true, 
    maintainAspectRatio: false,
    plugins: { legend: { position: 'top' }, title: { display: true, text: 'Project Risk Distribution' } } 
  };
  return <Doughnut data={data} options={options} />;
};

const ProjectsByCityChart = ({ data }) => {
  const options = { 
    responsive: true, 
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, title: { display: true, text: 'Projects by City' } }, 
    scales: { y: { beginAtZero: true } } 
  };
  return <Bar data={data} options={options} />;
};

const BudgetVsActualChart = ({ data }) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Budget vs Actual/Predicted Cost by Contractor' }
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Cost ($)' } },
      x: { title: { display: true, text: 'Contractor' } }
    }
  };
  return <Line data={data} options={options} />;
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

  // Process data for budget vs actual/prediction by contractor chart
  const contractorData = projects.reduce((acc, p) => {
    const contractor = p.Vendor || 'Unknown';
    if (!acc[contractor]) {
      acc[contractor] = {
        budgets: [],
        actuals: [],
        predictions: [],
        projects: []
      };
    }
    
    acc[contractor].budgets.push(p.Budget || 0);
    acc[contractor].projects.push(p.ProjectID);
    
    // Use actual cost for completed projects, predicted cost for others
    if (p.ProjectStatus === 'Completed' && p.ActualCost) {
      acc[contractor].actuals.push(p.ActualCost);
    } else if (p.PredictedCost) {
      acc[contractor].predictions.push(p.PredictedCost);
    }
    
    return acc;
  }, {});

  const contractors = Object.keys(contractorData);
  const contractorColors = {
    'Apex Construction': 'rgba(255, 99, 132, 1)',
    'Keystone Builders': 'rgba(54, 162, 235, 1)',
    'Precision Mechanical': 'rgba(255, 206, 86, 1)',
    'Stellar Renovations': 'rgba(75, 192, 192, 1)',
    'Summit Contractors': 'rgba(153, 102, 255, 1)'
  };

  const budgetVsActualData = {
    labels: contractors,
    datasets: [
      {
        label: 'Average Budget',
        data: contractors.map(contractor => {
          const budgets = contractorData[contractor].budgets;
          return budgets.length > 0 ? budgets.reduce((a, b) => a + b, 0) / budgets.length : 0;
        }),
        borderColor: 'rgba(128, 128, 128, 1)',
        backgroundColor: 'rgba(128, 128, 128, 0.1)',
        tension: 0.1,
        fill: false
      },
      {
        label: 'Average Actual Cost',
        data: contractors.map(contractor => {
          const actuals = contractorData[contractor].actuals;
          return actuals.length > 0 ? actuals.reduce((a, b) => a + b, 0) / actuals.length : null;
        }),
        borderColor: 'rgba(220, 53, 69, 1)',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        tension: 0.1,
        fill: false
      },
      {
        label: 'Average Predicted Cost',
        data: contractors.map(contractor => {
          const predictions = contractorData[contractor].predictions;
          return predictions.length > 0 ? predictions.reduce((a, b) => a + b, 0) / predictions.length : null;
        }),
        borderColor: 'rgba(40, 167, 69, 1)',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        tension: 0.1,
        fill: false
      }
    ]
  };

  return (
    <div className="row">
      {/* --- Left Column: KPIs --- */}
      <div className="col-lg-3">
        <KpiCard title="Total Projects" value={totalProjects} icon="📊" color="primary" />
        <KpiCard title="High Risk Projects" value={highRiskProjects} icon="⚠️" color="warning" />
        <KpiCard title="Total Budget" value={formatCurrency(totalBudget)} icon="💰" color="info" />
        <KpiCard title="Budget Variance" value={formatCurrency(totalBudgetVariance)} icon="📈" color={totalBudgetVariance > 0 ? 'danger' : 'success'} />
        
        {/* Project Risk Distribution Chart */}
        <div className="card mt-3">
          <div className="card-body" style={{ height: '300px' }}>
            <RiskDistributionChart data={riskChartData} />
          </div>
        </div>
      </div>

      {/* --- Right Column: Charts --- */}
      <div className="col-lg-9">
        {/* Budget vs Actual Chart */}
        <div className="card mb-4">
          <div className="card-body" style={{ height: '329px' }}>
            <BudgetVsActualChart data={budgetVsActualData} />
          </div>
        </div>
        
        {/* Projects by City Chart */}
        <div className="card mb-4">
          <div className="card-body" style={{ height: '329px' }}>
            <ProjectsByCityChart data={cityChartData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
