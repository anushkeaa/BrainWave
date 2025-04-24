import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

interface BackendStatusCheckProps {
  isReachable?: boolean;
}

export const BackendStatusCheck: React.FC<BackendStatusCheckProps> = ({ isReachable: propIsReachable }) => {
  const [isReachable, setIsReachable] = useState<boolean | null>(propIsReachable ?? null);
  const [isChecking, setIsChecking] = useState(false);

  const checkBackendStatus = async () => {
    setIsChecking(true);
    try {
      const response = await fetch('http://localhost:5000/api/status', { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      setIsReachable(response.ok);
    } catch (error) {
      console.error('Error checking backend status:', error);
      setIsReachable(false);
    } finally {
      setIsChecking(false);
    }
  };

  // Update internal state when prop changes
  useEffect(() => {
    if (propIsReachable !== undefined) {
      setIsReachable(propIsReachable);
    }
  }, [propIsReachable]);

  // Check status on initial render if prop not provided
  useEffect(() => {
    if (propIsReachable === undefined) {
      checkBackendStatus();
    }
  }, [propIsReachable]);

  const handleOpenBackendFolder = () => {
    // This will only work in Electron or similar environments
    // In a web browser, provide instructions instead
    alert('Please navigate to the src/backend folder and run: python simple_run.py');
  };

  const handleTryAlternativePort = async () => {
    setIsChecking(true);
    try {
      const response = await fetch('http://localhost:8000/api/status', { method: 'GET' });
      if (response.ok) {
        setIsReachable(true);
        alert('Backend found on port 8000! The app should now work correctly.');
      } else {
        alert('Backend not found on port 8000 either.');
        setIsReachable(false);
      }
    } catch (error) {
      alert('Backend not found on port 8000 either.');
      setIsReachable(false);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-6">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-medium">Backend Status</h2>
        <button 
          onClick={checkBackendStatus}
          className="flex items-center text-sm text-blue-600 hover:text-blue-800"
          disabled={isChecking}
        >
          <RefreshCw className={`w-4 h-4 mr-1 ${isChecking ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>
      
      <div className={`p-3 rounded-md ${isReachable ? 'bg-green-50' : 'bg-red-50'}`}>
        <p className={`font-medium ${isReachable ? 'text-green-800' : 'text-red-800'}`}>
          Backend server is {isReachable ? 'running' : 'not running'}
        </p>
        
        {!isReachable && (
          <div className="mt-2">
            <p className="text-gray-700 mb-2">
              Please start the Python backend server by running:
            </p>
            <div className="bg-gray-100 p-2 rounded font-mono text-sm mb-3">
              cd src/backend && python simple_run.py
            </div>
            
            <div className="flex flex-wrap gap-2">
              <button 
                onClick={checkBackendStatus}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm hover:bg-blue-200"
              >
                🔄 Reset Backend Connection
              </button>
              <button 
                onClick={handleTryAlternativePort}
                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-md text-sm hover:bg-purple-200"
              >
                🔍 Try Alternative Port (8000)
              </button>
              <button 
                onClick={handleOpenBackendFolder}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-md text-sm hover:bg-green-200"
              >
                📁 Open Backend Folder
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
