import React from 'react';
import './SolutionPanel.css';

interface SolutionPanelProps {
  solution?: string;
  isLoading?: boolean;
  error?: string;
}

const SolutionPanel: React.FC<SolutionPanelProps> = ({ 
  solution, 
  isLoading = false, 
  error 
}) => {
  const hasContent = solution || isLoading || error;

  if (!hasContent) {
    return (
      <div className="solution-panel-container">
        <div className="solution-panel empty">
          <div className="empty-state">
            <div className="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
                <path d="M19 15L19.74 18.26L23 19L19.74 19.74L19 23L18.26 19.74L15 19L18.26 18.26L19 15Z" fill="currentColor"/>
              </svg>
            </div>
            <h3 className="empty-title">Ready to Solve</h3>
            <p className="empty-description">
              Upload an image or take a screenshot to get your math solution
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="solution-panel-container">
      <div className="solution-panel">
        <div className="solution-header">
          <h2 className="solution-title">
            {isLoading ? 'Analyzing Question...' : error ? 'Error' : 'Solution'}
          </h2>
          {isLoading && (
            <div className="loading-indicator">
              <div className="spinner"></div>
            </div>
          )}
        </div>

        <div className="solution-content">
          {isLoading && (
            <div className="loading-content">
              <div className="loading-text">
                <p>🔍 Analyzing your math question...</p>
                <p>⚡ Generating step-by-step solution...</p>
                <p>📝 Preparing the explanation...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="error-content">
              <div className="error-icon">⚠️</div>
              <div className="error-text">
                <h4>Something went wrong</h4>
                <p>{error}</p>
              </div>
            </div>
          )}

          {solution && !isLoading && !error && (
            <div className="solution-text">
              {solution.split('\n').map((line, index) => {
                // Skip empty lines
                if (line.trim() === '') {
                  return <div key={index} className="solution-spacer"></div>;
                }
                
                // Check for step numbers or headers
                const isStep = /^\d+\./.test(line.trim());
                const isHeader = line.includes(':') && line.length < 100;
                
                return (
                  <p 
                    key={index} 
                    className={`solution-line ${isStep ? 'step' : ''} ${isHeader ? 'header' : ''}`}
                  >
                    {line}
                  </p>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SolutionPanel;
