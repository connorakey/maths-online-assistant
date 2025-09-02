import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import Explaination from './components/Explaination';
import Header from './components/Header';
import MathQuestionForm from './components/MathQuestionForm';
import SolutionPanel from './components/SolutionPanel';
import Settings, { type ScreenshotCoordinates } from './components/Settings';
import { RequestType } from './types/request';
import './App.css';

function App() {
  const [solutionData, setSolutionData] = useState<{
    solution?: string;
    isLoading?: boolean;
    error?: string;
  }>({});
  const [showSettings, setShowSettings] = useState(false);

  const handleScreenshotMode = async () => {
    try {
      // Get screenshot coordinates from settings
      const coordinates = await invoke<ScreenshotCoordinates>('get_screenshot_coordinates');
      
      // Capture screenshot using coordinates
      const screenshotResult = await invoke<{
        success: boolean;
        base64_data: string;
        error?: string;
      }>('capture_screenshot', {
        area: {
          x1: coordinates.x1,
          y1: coordinates.y1,
          x2: coordinates.x2,
          y2: coordinates.y2
        }
      });

      if (screenshotResult.success) {
        // Process the screenshot with AI
        console.log('Screenshot captured successfully, processing with AI...');
        
        // Get settings for API configuration
        const settings = await invoke<{
          base_url: string;
          api_key: string;
        }>('get_settings');
        
        console.log('Settings loaded:', settings);
        
        // Send to backend for processing
        const requestParams = {
          request: {
            image_b64: screenshotResult.base64_data,
            api_key: settings.api_key,
            request_type: 'StepByStep'
          },
          baseUrl: settings.base_url
        };
        
        console.log('Sending request with params:', requestParams);
        
        const apiResponse = await invoke<{
          success: boolean;
          response: string;
        }>('send_openai_request', requestParams);
        
        if (apiResponse.success) {
          setSolutionData({
            solution: apiResponse.response
          });
        } else {
          setSolutionData({
            error: `API request failed: ${apiResponse.response}`
          });
        }
      } else {
        setSolutionData({
          error: `Screenshot failed: ${screenshotResult.error || 'Unknown error'}`
        });
      }
    } catch (error) {
      console.error('Screenshot error:', error);
      setSolutionData({
        error: `Failed to take screenshot: ${error}`
      });
    }
  };

  const handleFormSubmit = async (data: {
    requestType: RequestType;
    imageData?: string;
    useScreenshot: boolean;
  }) => {
    console.log('Form submitted:', {
      requestType: data.requestType,
      useScreenshot: data.useScreenshot,
      hasImageData: !!data.imageData
    });

    // Set loading state
    setSolutionData({ isLoading: true });

    try {
      if (data.useScreenshot) {
        // Handle screenshot mode
        console.log('Taking screenshot...');
        await handleScreenshotMode();
      } else if (data.imageData) {
        // Handle uploaded image
        console.log('Processing uploaded image...');
        
        // Get settings for API configuration
        const settings = await invoke<{
          base_url: string;
          api_key: string;
        }>('get_settings');
        
        console.log('Settings loaded for upload:', settings);
        
        // Determine request type based on form selection
        const requestType = data.requestType === RequestType.StepByStep ? 'StepByStep' : 'FinalAnswer';
        
        // Send to backend for processing
        const requestParams = {
          request: {
            image_b64: data.imageData,
            api_key: settings.api_key,
            request_type: requestType
          },
          baseUrl: settings.base_url
        };
        
        console.log('Sending upload request with params:', requestParams);
        
        const apiResponse = await invoke<{
          success: boolean;
          response: string;
        }>('send_openai_request', requestParams);
        
        if (apiResponse.success) {
          setSolutionData({
            solution: apiResponse.response
          });
        } else {
          setSolutionData({
            error: `API request failed: ${apiResponse.response}`
          });
        }
      }
    } catch (error) {
      console.error('API request error:', error);
      setSolutionData({
        error: `Failed to process request: ${error}`
      });
    }
  };

  return (
    <>
      <Header onSettingsClick={() => setShowSettings(true)} />
      <div className="app-container">
        <div className="main-content">
          <div className="left-panel">
            <Explaination />
          </div>
          <div className="right-panel">
            <MathQuestionForm onSubmit={handleFormSubmit} />
          </div>
        </div>
        <div className="solution-section">
          <SolutionPanel 
            solution={solutionData.solution}
            isLoading={solutionData.isLoading}
            error={solutionData.error}
          />
        </div>
      </div>
      {showSettings && (
        <Settings onClose={() => setShowSettings(false)} />
      )}
    </>
  )
}

export default App
