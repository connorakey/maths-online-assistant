import React, { useState } from 'react';
import RequestTypeDropdown from './RequestTypeDropdown';
import { RequestType } from '../types/request';
import UploadBox from './UploadBox';
import './MathQuestionForm.css';

interface MathQuestionFormProps {
  onSubmit: (data: {
    requestType: RequestType;
    imageData?: string;
    useScreenshot: boolean;
  }) => void;
}

const MathQuestionForm: React.FC<MathQuestionFormProps> = ({ onSubmit }) => {
  const [requestType, setRequestType] = useState<RequestType>(RequestType.StepByStep);
  const [useScreenshot, setUseScreenshot] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageUpload = (base64Data: string) => {
    setUploadedImage(base64Data);
    setError(null);
  };

  const handleUploadError = (error: string) => {
    setError(error);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Check if either screenshot is enabled or an image is uploaded
    if (!useScreenshot && !uploadedImage) {
      setError('Please either enable screenshot or upload an image');
      return;
    }

    // If screenshot is enabled, don't require uploaded image
    if (useScreenshot) {
      onSubmit({
        requestType,
        useScreenshot: true,
      });
      return;
    }

    // If image is uploaded, use that
    if (uploadedImage) {
      onSubmit({
        requestType,
        imageData: uploadedImage,
        useScreenshot: false,
      });
      return;
    }
  };

  const canSubmit = useScreenshot || uploadedImage;

  return (
    <div className="math-question-form-container">
      <form className="math-question-form" onSubmit={handleSubmit}>
        <h2 className="form-title">Math Question Solver</h2>
        
        <RequestTypeDropdown 
          value={requestType}
          onChange={setRequestType}
        />

        <div className="screenshot-option">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={useScreenshot}
              onChange={(e) => setUseScreenshot(e.target.checked)}
              className="checkbox-input"
            />
            <span className="checkbox-text">
              Use screenshot mode (select area on screen)
            </span>
          </label>
        </div>

        {!useScreenshot && (
          <div className="upload-section">
            <h3 className="upload-title">Or upload an image:</h3>
            <UploadBox 
              onImageUpload={handleImageUpload}
              onError={handleUploadError}
              isUploaded={!!uploadedImage}
            />
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button 
          type="submit" 
          className={`submit-button ${canSubmit ? 'enabled' : 'disabled'}`}
          disabled={!canSubmit}
        >
          {useScreenshot ? 'Take Screenshot & Solve' : 'Solve Question'}
        </button>
      </form>
    </div>
  );
};

export default MathQuestionForm;
