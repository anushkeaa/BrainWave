import React, { useState, useEffect } from 'react';

export function DirectWebcamCheck() {
  const [hasWebcam, setHasWebcam] = useState<boolean | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function checkWebcamDirectly() {
      try {
        // Request camera permission directly from the browser
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        
        // If we get here, webcam is available
        console.log("Webcam permission granted directly by browser");
        setHasWebcam(true);
        
        // Stop the tracks to release the camera
        stream.getTracks().forEach(track => track.stop());
      } catch (err) {
        console.error("Error accessing webcam directly:", err);
        setHasWebcam(false);
        setErrorMessage(err instanceof Error ? err.message : 'Unknown error');
      }
    }
    
    checkWebcamDirectly();
  }, []);

  if (hasWebcam === null) {
    return <div className="text-sm text-gray-500">Checking browser webcam access...</div>;
  }

  return (
    <div className={`text-sm p-2 border rounded ${hasWebcam ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
      <div className="flex items-center">
        <div className={`w-3 h-3 rounded-full mr-2 ${hasWebcam ? 'bg-green-500' : 'bg-red-500'}`}></div>
        <div>
          <span className="font-medium">Browser Webcam:</span> 
          {hasWebcam ? 
            ' ✅ Browser can access webcam directly' : 
            ' ❌ Browser cannot access webcam'}
        </div>
      </div>
      
      {!hasWebcam && errorMessage && (
        <div className="mt-1 text-xs text-red-600">{errorMessage}</div>
      )}
      
      {hasWebcam && (
        <div className="mt-1 text-xs text-green-600">
          Your browser has direct webcam access. If the app still can't detect your webcam, 
          use the "Override Webcam Detection" option above.
        </div>
      )}
    </div>
  );
}
