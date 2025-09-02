import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './Settings.css';

export interface ScreenshotCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface SettingsData {
  api_key: string;
  screenshot_coords: ScreenshotCoordinates;
  base_url: string;
}

interface SettingsProps {
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const [settings, setSettings] = useState<SettingsData>({
    api_key: '',
    screenshot_coords: { x1: 0, y1: 0, x2: 100, y2: 100 },
    base_url: 'http://localhost:3000'
  });

  const [adminPassword, setAdminPassword] = useState('');
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [tempSettings, setTempSettings] = useState<SettingsData>(settings);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Password change state
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [passwordChange, setPasswordChange] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const loadedSettings = await invoke<SettingsData>('get_settings');
      setSettings(loadedSettings);
      setTempSettings(loadedSettings);
    } catch (err) {
      console.error('Failed to load settings:', err);
      setError('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyAdminPassword = async (password: string): Promise<boolean> => {
    try {
      // Try to verify with any section - if admin password works for one, it works for all
      const isValid = await invoke<boolean>('verify_settings_password', { 
        section: 'apiKey', 
        password 
      });
      return isValid;
    } catch (err) {
      console.error('Password verification failed:', err);
      return false;
    }
  };

  const handleUnlock = async () => {
    if (!adminPassword) {
      setError('Please enter the admin password');
      return;
    }

    setError('');
    const isValid = await verifyAdminPassword(adminPassword);
    
    if (isValid) {
      setIsUnlocked(true);
      setSuccess('Settings unlocked successfully!');
      setAdminPassword(''); // Clear password for security
    } else {
      setError('Invalid admin password');
    }
  };

  const handleSave = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      await invoke('save_settings', { 
        settings: tempSettings,
        unlockedSections: ['apiKey', 'screenshotCoords'] // Admin can save all sections
      });
      
      setSettings(tempSettings);
      setSuccess('Settings saved successfully!');
      
      // Auto-close after successful save
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCoordinateChange = (coord: keyof ScreenshotCoordinates, value: string) => {
    const numValue = parseInt(value) || 0;
    setTempSettings(prev => ({
      ...prev,
      screenshot_coords: {
        ...prev.screenshot_coords,
        [coord]: numValue
      }
    }));
  };

  const handlePasswordChange = async () => {
    if (!passwordChange.currentPassword || !passwordChange.newPassword || !passwordChange.confirmPassword) {
      setError('Please fill in all password fields');
      return;
    }

    if (passwordChange.newPassword !== passwordChange.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (passwordChange.newPassword.length < 6) {
      setError('New password must be at least 6 characters long');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      await invoke('change_settings_password', {
        section: 'apiKey', // Using apiKey section since we have unified password
        oldPassword: passwordChange.currentPassword,
        newPassword: passwordChange.newPassword
      });

      setSuccess('Master password changed successfully!');
      setPasswordChange({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowPasswordChange(false);

      // Auto-close settings after password change
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      console.error('Failed to change password:', err);
      setError(`Failed to change password: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  if (isLoading && Object.keys(settings).length === 0) {
    return (
      <div className="settings-overlay">
        <div className="settings-modal">
          <div className="loading">Loading settings...</div>
        </div>
      </div>
    );
  }

  // Show unlock screen if not unlocked
  if (!isUnlocked) {
    return (
      <div className="settings-overlay">
        <div className="settings-modal">
          <div className="settings-header">
            <h2>Settings</h2>
            <button className="close-button" onClick={onClose}>×</button>
          </div>
          
          <div className="settings-content">
            <div className="unlock-section">
              <h3>🔒 Admin Access Required</h3>
              <p>Enter the admin password to access settings</p>
              
              {error && (
                <div className="error-message">
                  {error}
                  <button className="clear-message" onClick={clearMessages}>×</button>
                </div>
              )}
              
              <div className="password-input">
                <input
                  type="password"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleUnlock()}
                  placeholder="Enter admin password"
                  autoFocus
                />
                <button onClick={handleUnlock}>Unlock Settings</button>
              </div>
              
              <small className="help-text">
                Default password: <code>admin123</code>
              </small>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show settings when unlocked
  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          {error && (
            <div className="error-message">
              {error}
              <button className="clear-message" onClick={clearMessages}>×</button>
            </div>
          )}
          
          {success && (
            <div className="success-message">
              {success}
              <button className="clear-message" onClick={clearMessages}>×</button>
            </div>
          )}

          {/* Base URL Setting */}
          <div className="setting-section">
            <h3>Backend URL</h3>
            <div className="setting-field">
              <label htmlFor="base_url">Server URL:</label>
              <input
                id="base_url"
                type="text"
                value={tempSettings.base_url}
                onChange={(e) => setTempSettings(prev => ({ ...prev, base_url: e.target.value }))}
                placeholder="http://localhost:3000"
              />
              <small>URL where your backend server is running</small>
            </div>
          </div>

          {/* API Key Setting */}
          <div className="setting-section">
            <h3>OpenAI API Key</h3>
            <div className="setting-field">
              <label htmlFor="api_key">API Key:</label>
              <input
                id="api_key"
                type="password"
                value={tempSettings.api_key}
                onChange={(e) => setTempSettings(prev => ({ ...prev, api_key: e.target.value }))}
                placeholder="Enter your OpenAI API key"
              />
              <small>Your API key is stored securely and only used for making requests</small>
            </div>
          </div>

          {/* Screenshot Coordinates Setting */}
          <div className="setting-section">
            <h3>Screenshot Coordinates</h3>
            <div className="coordinates-grid">
              <div className="coordinate-field">
                <label htmlFor="x1">Top-Left X:</label>
                <input
                  id="x1"
                  type="number"
                  value={tempSettings.screenshot_coords.x1}
                  onChange={(e) => handleCoordinateChange('x1', e.target.value)}
                />
              </div>
              <div className="coordinate-field">
                <label htmlFor="y1">Top-Left Y:</label>
                <input
                  id="y1"
                  type="number"
                  value={tempSettings.screenshot_coords.y1}
                  onChange={(e) => handleCoordinateChange('y1', e.target.value)}
                />
              </div>
              <div className="coordinate-field">
                <label htmlFor="x2">Bottom-Right X:</label>
                <input
                  id="x2"
                  type="number"
                  value={tempSettings.screenshot_coords.x2}
                  onChange={(e) => handleCoordinateChange('x2', e.target.value)}
                />
              </div>
              <div className="coordinate-field">
                <label htmlFor="y2">Bottom-Right Y:</label>
                <input
                  id="y2"
                  type="number"
                  value={tempSettings.screenshot_coords.y2}
                  onChange={(e) => handleCoordinateChange('y2', e.target.value)}
                />
              </div>
              <small className="coordinates-help">
                These coordinates define the screenshot area. 
                Set 4 points to capture the exact region of your screen.
              </small>
            </div>
          </div>

          {/* Password Management Section */}
          <div className="setting-section">
            <h3>Security</h3>
            <div className="setting-field">
              <button 
                className="secondary-button"
                onClick={() => setShowPasswordChange(!showPasswordChange)}
              >
                {showPasswordChange ? 'Cancel Password Change' : 'Change Master Password'}
              </button>
            </div>

            {showPasswordChange && (
              <div className="password-change-section">
                <div className="setting-field">
                  <label htmlFor="current-password">Current Password:</label>
                  <input
                    id="current-password"
                    type="password"
                    value={passwordChange.currentPassword}
                    onChange={(e) => setPasswordChange(prev => ({ ...prev, currentPassword: e.target.value }))}
                    placeholder="Enter current master password"
                  />
                </div>
                <div className="setting-field">
                  <label htmlFor="new-password">New Password:</label>
                  <input
                    id="new-password"
                    type="password"
                    value={passwordChange.newPassword}
                    onChange={(e) => setPasswordChange(prev => ({ ...prev, newPassword: e.target.value }))}
                    placeholder="Enter new password (min 6 characters)"
                  />
                </div>
                <div className="setting-field">
                  <label htmlFor="confirm-password">Confirm New Password:</label>
                  <input
                    id="confirm-password"
                    type="password"
                    value={passwordChange.confirmPassword}
                    onChange={(e) => setPasswordChange(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    placeholder="Confirm new password"
                  />
                </div>
                <div className="password-change-actions">
                  <button 
                    className="primary-button"
                    onClick={handlePasswordChange}
                    disabled={isLoading}
                  >
                    {isLoading ? 'Changing...' : 'Change Password'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="settings-footer">
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button 
            className="save-button primary" 
            onClick={handleSave} 
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
