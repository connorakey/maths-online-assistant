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
        // TODO: Send to AI for processing
        setSolutionData({
          solution: `Step-by-Step Solution (Screenshot Mode):\n\nScreenshot captured from coordinates (${coordinates.x1}, ${coordinates.y1}) to (${coordinates.x2}, ${coordinates.y2})\n\n1. First, identify the problem type...\n2. Apply the appropriate formula...\n3. Solve step by step...\n4. Check your answer.`
        });
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

  const handleFormSubmit = (data: {
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

    if (data.useScreenshot) {
      // Handle screenshot mode
      console.log('Taking screenshot...');
      handleScreenshotMode();
    } else if (data.imageData) {
      // Handle uploaded image
      console.log('Processing uploaded image...');
      // TODO: Implement image processing
      // invoke('process_uploaded_image', { base64Input: data.imageData })
      
      // For now, simulate loading
      setTimeout(() => {
        setSolutionData({
          solution: `Step-by-Step Solution (Upload Mode):\n\n1. Analyzing uploaded image...\n2. Identifying mathematical expressions...\n3. Applying solution method...\n4. Final answer: [Solution will appear here]`
        });
      }, 3000);
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
