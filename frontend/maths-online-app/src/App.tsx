import { useState } from 'react';
import Explaination from './components/Explaination';
import Header from './components/Header';
import MathQuestionForm from './components/MathQuestionForm';
import SolutionPanel from './components/SolutionPanel';
import { RequestType } from './types/request';
import './App.css';

function App() {
  const [solutionData, setSolutionData] = useState<{
    solution?: string;
    isLoading?: boolean;
    error?: string;
  }>({});

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
      // TODO: Implement screenshot functionality
      // invoke('capture_screenshot', { area: screenshotArea })
      
      // For now, simulate loading
      setTimeout(() => {
        setSolutionData({
          solution: `Step-by-Step Solution (Screenshot Mode):\n\n1. First, identify the problem type...\n2. Apply the appropriate formula...\n3. Solve step by step...\n4. Check your answer.`
        });
      }, 3000);
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
      <Header />
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
    </>
  )
}

export default App
