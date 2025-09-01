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
  apiKey: string;
  screenshot_coords: ScreenshotCoordinates;
  baseUrl: string;
}

interface SettingsProps {
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const [settings, setSettings] = useState<SettingsData>({
    apiKey: '',
    screenshot_coords: { x1: 0, y1: 0, x2: 100, y2: 100 },
    baseUrl: 'http://localhost:8080'
  });

  const [passwords, setPasswords] = useState({
    apiKey: '',
    screenshotCoords: ''
  });

  const [showSettings, setShowSettings] = useState({
    apiKey: false,
    screenshotCoords: false
  });

  const [tempSettings, setTempSettings] = useState<SettingsData>(settings);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

  const verifyPassword = async (section: 'apiKey' | 'screenshotCoords', password: string): Promise<boolean> => {
    try {
      const isValid = await invoke<boolean>('verify_settings_password', { 
        section, 
        password 
      });
      return isValid;
    } catch (err) {
      console.error('Password verification failed:', err);
      return false;
    }
  };

  const handleUnlock = async (section: 'apiKey' | 'screenshotCoords') => {
    const password = passwords[section];
    if (!password) {
      setError('Please enter a password');
      return;
    }

    setError('');
    const isValid = await verifyPassword(section, password);
    
    if (isValid) {
      setShowSettings(prev => ({ ...prev, [section]: true }));
      setSuccess(`${section === 'apiKey' ? 'API Key' : 'Screenshot Coordinates'} section unlocked`);
    } else {
      setError('Invalid password');
    }
  };

  const handleSave = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      // Only save sections that are unlocked
      const sectionsToSave: string[] = [];
      if (showSettings.apiKey) sectionsToSave.push('apiKey');
      if (showSettings.screenshotCoords) sectionsToSave.push('screenshotCoords');

      if (sectionsToSave.length === 0) {
        setError('No sections are unlocked for saving');
        return;
      }

      await invoke('save_settings', { 
        settings: tempSettings,
        unlockedSections: sectionsToSave
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

          {/* Base URL Setting (No password protection) */}
          <div className="setting-section">
            <h3>Backend URL</h3>
            <div className="setting-field">
              <label htmlFor="baseUrl">Server URL:</label>
              <input
                id="baseUrl"
                type="text"
                value={tempSettings.baseUrl}
                onChange={(e) => setTempSettings(prev => ({ ...prev, baseUrl: e.target.value }))}
                placeholder="http://localhost:8080"
              />
            </div>
          </div>

          {/* API Key Setting */}
          <div className="setting-section">
            <h3>OpenAI API Key</h3>
            {!showSettings.apiKey ? (
              <div className="locked-section">
                <p>🔒 This section is password protected</p>
                <div className="password-input">
                  <input
                    type="password"
                    placeholder="Enter password to view/edit API key"
                    value={passwords.apiKey}
                    onChange={(e) => setPasswords(prev => ({ ...prev, apiKey: e.target.value }))}
                    onKeyPress={(e) => e.key === 'Enter' && handleUnlock('apiKey')}
                  />
                  <button onClick={() => handleUnlock('apiKey')}>Unlock</button>
                </div>
              </div>
            ) : (
              <div className="setting-field">
                <label htmlFor="apiKey">API Key:</label>
                <input
                  id="apiKey"
                  type="password"
                  value={tempSettings.apiKey}
                  onChange={(e) => setTempSettings(prev => ({ ...prev, apiKey: e.target.value }))}
                  placeholder="Enter your OpenAI API key"
                />
                <small>Your API key is stored securely and only used for making requests.</small>
              </div>
            )}
          </div>

          {/* Screenshot Coordinates Setting */}
          <div className="setting-section">
            <h3>Screenshot Coordinates</h3>
            {!showSettings.screenshotCoords ? (
              <div className="locked-section">
                <p>🔒 This section is password protected</p>
                <div className="password-input">
                  <input
                    type="password"
                    placeholder="Enter password to view/edit coordinates"
                    value={passwords.screenshotCoords}
                    onChange={(e) => setPasswords(prev => ({ ...prev, screenshotCoords: e.target.value }))}
                    onKeyPress={(e) => e.key === 'Enter' && handleUnlock('screenshotCoords')}
                  />
                  <button onClick={() => handleUnlock('screenshotCoords')}>Unlock</button>
                </div>
              </div>
            ) : (
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
            )}
          </div>
        </div>

        <div className="settings-footer">
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button 
            className="save-button" 
            onClick={handleSave} 
            disabled={isLoading || (!showSettings.apiKey && !showSettings.screenshotCoords)}
          >
            {isLoading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
