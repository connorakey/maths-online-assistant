import React, { useState, useRef } from 'react';
import './UploadBox.css';

interface UploadBoxProps {
  onImageUpload: (base64Data: string) => void;
  onError?: (error: string) => void;
}

const UploadBox: React.FC<UploadBoxProps> = ({ onImageUpload, onError }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      onError?.('Please select an image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      onError?.('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    const reader = new FileReader();

    reader.onload = (e) => {
      const result = e.target?.result as string;
      if (result) {
        onImageUpload(result);
      }
      setIsUploading(false);
    };

    reader.onerror = () => {
      onError?.('Failed to read file');
      setIsUploading(false);
    };

    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-box-container">
      <div
        className={`upload-box ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          {isUploading ? (
            <div className="upload-loading">
              <div className="spinner"></div>
              <p>Processing image...</p>
            </div>
          ) : (
            <>
              <div className="upload-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/>
                </svg>
              </div>
              <h3 className="upload-title">Upload Math Question</h3>
              <p className="upload-description">
                Drag and drop your PNG image here, or click to browse
              </p>
              <p className="upload-hint">
                Supports PNG, JPG, JPEG • Max 10MB
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadBox;
