import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getProjects } from './services/api';
import Dashboard from './components/Dashboard';
import Filters from './components/Filters';
import ProjectTable from './components/ProjectTable';
import ProjectModal from './components/ProjectModal';
import './App.css';

function App() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'Budget', direction: 'descending' });
  const [selectedProject, setSelectedProject] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchProjects = useCallback(async (appliedFilters) => {
    setLoading(true);
    const data = await getProjects(appliedFilters);
    setProjects(data);
    setLoading(false);
  }, []);

  useEffect(() => {
    const appliedFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== '')
    );
    fetchProjects(appliedFilters);
  }, [filters, fetchProjects]);

  const handleFilterChange = (name, value) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value
    }));
  };

  const sortedProjects = useMemo(() => {
    let sortableProjects = [...projects];
    if (sortConfig !== null) {
      sortableProjects.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableProjects;
  }, [projects, sortConfig]);

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const openModal = (project) => {
    setSelectedProject(project);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedProject(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-title">Project Lighthouse</h1>
      </header>
      <main className="container-fluid p-4">
        <Dashboard projects={projects} />
        <div className="card mt-4">
          <div className="card-body">
            <h5 className="card-title">All Projects</h5>
            <Filters filters={filters} onFilterChange={handleFilterChange} />
            {loading ? (
              <p className="loading-text">Loading Projects...</p>
            ) : (
              <ProjectTable 
                projects={sortedProjects} 
                requestSort={requestSort} 
                sortConfig={sortConfig}
                onRowClick={openModal}
              />
            )}
          </div>
        </div>
        {isModalOpen && <ProjectModal project={selectedProject} onClose={closeModal} />}
      </main>
    </div>
  );
}

export default App;