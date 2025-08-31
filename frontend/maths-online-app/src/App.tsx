import Explaination from './components/Explaination';
import Header from './components/Header';
import UploadBox from './components/UploadBox';

function App() {
  const handleImageUpload = (base64Data: string) => {
    console.log('Image uploaded:', base64Data.substring(0, 100) + '...');
    // add tauri functionality later
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    // add tauri functionality later
  };

  return (
    <>
      <Header />
      <Explaination />
      <div style={{ padding: '0 24px', maxWidth: '800px', margin: '0 auto' }}>
        <UploadBox 
          onImageUpload={handleImageUpload}
          onError={handleUploadError}
        />
      </div>
    </>
  )
}

export default App
