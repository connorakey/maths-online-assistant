import React from 'react';
import './Header.css';

interface HeaderProps {
  onSettingsClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onSettingsClick }) => {
  return (
    <header className="app-header">
      <div className="header-container">
        <div className="header-left">
          <div className="logo-section">
            <div className="logo-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="currentColor"/>
                <path d="M19 15L19.74 18.26L23 19L19.74 19.74L19 23L18.26 19.74L15 19L18.26 18.26L19 15Z" fill="currentColor"/>
              </svg>
            </div>
            <h1 className="app-title">Maths Online Tutor</h1>
          </div>
        </div>

        <div className="header-right">
          <nav className="header-nav">
            <ul className="nav-list">
              <li className="nav-item">
                <button className="nav-button active">
                  <span className="nav-icon">🏠</span>
                  <span>Home</span>
                </button>
              </li>
              <li className="nav-item">
                <button className="nav-button" onClick={onSettingsClick}>
                  <span className="nav-icon">⚙️</span>
                  <span>Settings</span>
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;