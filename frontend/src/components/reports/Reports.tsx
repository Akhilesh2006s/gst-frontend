import React from 'react';
import { Link } from 'react-router-dom';

const Reports: React.FC = () => {
  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">
          <i className="fas fa-chart-bar me-2"></i>
          Reports
        </h1>
      </div>
      
      <div className="card">
        <div className="card-body text-center py-5">
          <i className="fas fa-chart-bar fa-3x text-muted mb-3"></i>
          <h4>Business Reports</h4>
          <p className="text-muted">This feature will be implemented soon.</p>
          <Link to="/dashboard" className="btn btn-primary">
            <i className="fas fa-arrow-left me-1"></i>Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Reports;

