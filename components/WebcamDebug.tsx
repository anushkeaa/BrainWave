import React, { useState, useEffect } from 'react';
import { RefreshCw, Camera } from 'lucide-react';

interface WebcamDebugProps {
  handleForceDisconnect?: () => Promise<void>;
}

export const WebcamDebug: React.FC<WebcamDebugProps> = ({ handleForceDisconnect }) => {
  const [webcamAvailable, setWebcamAvailable] = useState<boolean | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [deviceList, setDeviceList] = useState<MediaDeviceInfo[]>([]);

  const checkWebcam = async () => {
    setIsChecking(true);
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setDeviceList(videoDevices);
      
      if (videoDevices.length > 0) {
        try {
          // Try to access the camera
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          // Release tracks
          stream.getTracks().forEach(track => track.stop());
          setWebcamAvailable(true);
        } catch (err) {
          console.error("Could see camera but access denied:", err);
          setWebcamAvailable(false);
        }
      } else {
        setWebcamAvailable(false);
      }
    } catch (error) {
      console.error('Error checking webcam:', error);
      setWebcamAvailable(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkWebcam();
  }, []);

  const handleForceEnableWebcam = () => {
    alert('This will force enable the webcam for brain activity detection, skipping all tests. The page may reload.');
    // Here you would set a flag in localStorage and reload the page
    localStorage.setItem('forceWebcam', 'true');
    window.location.reload();
  };

  const runWebcamTest = async () => {
    setIsChecking(true);
    try {
      // Create a temporary video element to test webcam
      const video = document.createElement('video');
      video.style.position = 'fixed';
      video.style.top = '0';
      video.style.left = '0';
      video.style.width = '160px';
      video.style.height = '120px';
      video.style.zIndex = '9999';
      document.body.appendChild(video);
      
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      video.onloadedmetadata = () => {
        video.play();
        setWebcamAvailable(true);
        
        // Remove after 5 seconds
        setTimeout(() => {
          stream.getTracks().forEach(track => track.stop());
          document.body.removeChild(video);
        }, 5000);
      };
    } catch (error) {
      console.error('Webcam test failed:', error);
      setWebcamAvailable(false);
      alert('Failed to access webcam: ' + error.message);
    } finally {
      setIsChecking(false);
    }
  };

  const handleEmergencyReset = () => {
    // Force enable webcam
    handleForceEnableWebcam();
    
    // Call force disconnect if available
    if (handleForceDisconnect) {
      handleForceDisconnect();
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-medium">Webcam Status</h2>
        <button 
          onClick={checkWebcam}
          className="flex items-center text-sm text-blue-600 hover:text-blue-800"
          disabled={isChecking}
        >
          <RefreshCw className={`w-4 h-4 mr-1 ${isChecking ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className={`p-3 rounded-md mb-3 ${
        webcamAvailable === null 
          ? 'bg-gray-50' 
          : webcamAvailable 
            ? 'bg-green-50' 
            : 'bg-red-50'
      }`}>
        <p className={`font-medium ${
          webcamAvailable === null 
            ? 'text-gray-800' 
            : webcamAvailable 
              ? 'text-green-800' 
              : 'text-red-800'
        }`}>
          Webcam Status:
          {webcamAvailable === null 
            ? ' Checking...' 
            : webcamAvailable 
              ? ' ✅ Detected' 
              : ' ❌ Not detected or access denied'}
        </p>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-800 mt-2"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
        
        {showDetails && (
          <div className="mt-2 text-sm text-gray-700">
            <p>Found {deviceList.length} video devices:</p>
            <ul className="list-disc pl-5 mt-1">
              {deviceList.map((device, i) => (
                <li key={i}>{device.label || `Camera ${i+1}`}</li>
              ))}
              {deviceList.length === 0 && (
                <li>No video devices found</li>
              )}
            </ul>
          </div>
        )}
      </div>
      
      <div className="mb-3">
        <p className="text-sm text-gray-700 mb-2">
          Override Webcam Detection (Use if webcam works in test but not in UI)
        </p>
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={handleForceEnableWebcam}
            className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-md text-sm hover:bg-yellow-200"
          >
            🚀 Force Enable Webcam & Skip Tests
          </button>
          <button 
            onClick={runWebcamTest}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm hover:bg-blue-200"
          >
            🎥 Run Webcam Test Directly
          </button>
        </div>
      </div>
      
      <p className="text-xs text-gray-500">
        Make sure Python backend is running first: python simple_run.py
      </p>
      
      <div className="mt-4 border-t pt-3">
        <button 
          onClick={handleEmergencyReset}
          className="px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm hover:bg-red-200 w-full"
        >
          🚨 Emergency Reset (If Nothing Works)
        </button>
      </div>
    </div>
  );
};
