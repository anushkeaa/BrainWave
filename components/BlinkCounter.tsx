import React, { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface BlinkCounterProps {
  isConnected: boolean;
  mentalState: any;
  detectionMode: 'simulation' | 'webcam';
}

export function BlinkCounter({ isConnected, mentalState, detectionMode }: BlinkCounterProps) {
  const [totalBlinks, setTotalBlinks] = useState(0);
  const [leftBlinks, setLeftBlinks] = useState(0);
  const [rightBlinks, setRightBlinks] = useState(0);
  const [justBlinked, setJustBlinked] = useState(false);

  // Track blinks based on mental state changes
  useEffect(() => {
    if (!isConnected || detectionMode !== 'webcam' || !mentalState) return;

    // Detect changes in mental state as potential blinks
    const state = mentalState.state.toLowerCase();
    
    // Only count as a blink if confidence is high enough
    if (mentalState.confidence > 0.6) {
      if (state === 'left') {
        setRightBlinks(prev => prev + 1); // Right eye blink means left brain thinking
        setTotalBlinks(prev => prev + 1);
        flashBlinkAnimation();
      } else if (state === 'right') {
        setLeftBlinks(prev => prev + 1); // Left eye blink means right brain thinking
        setTotalBlinks(prev => prev + 1);
        flashBlinkAnimation();
      }
    }
  }, [mentalState, isConnected, detectionMode]);

  // Animation for blink
  const flashBlinkAnimation = () => {
    setJustBlinked(true);
    setTimeout(() => setJustBlinked(false), 300);
  };

  if (!isConnected || detectionMode !== 'webcam') {
    return null;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center mb-4">
        {justBlinked ? (
          <EyeOff className="w-6 h-6 text-purple-500 animate-pulse" />
        ) : (
          <Eye className="w-6 h-6 text-blue-500" />
        )}
        <h2 className="text-lg font-semibold ml-2">Blink Counter</h2>
      </div>
      
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-3xl font-bold text-blue-600">{totalBlinks}</div>
          <div className="text-sm text-gray-600">Total Blinks</div>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-3xl font-bold text-green-600">{leftBlinks}</div>
          <div className="text-sm text-gray-600">Left Eye Blinks</div>
          <div className="text-xs text-gray-500">(Right Brain)</div>
        </div>
        
        <div className="bg-purple-50 p-3 rounded-lg">
          <div className="text-3xl font-bold text-purple-600">{rightBlinks}</div>
          <div className="text-sm text-gray-600">Right Eye Blinks</div>
          <div className="text-xs text-gray-500">(Left Brain)</div>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-2 rounded">
        <p><strong>Note:</strong> This counts eye blinks detected by the webcam. Try blinking distinctly with your left or right eye to see the counters change.</p>
      </div>
    </div>
  );
}
