import React from 'react';
import { Brain, ArrowLeft, ArrowRight, Activity } from 'lucide-react';
import type { MentalState } from '../types/eeg';

interface MentalStateDisplayProps {
  mentalState: MentalState | null;
}

export function MentalStateDisplay({ mentalState }: MentalStateDisplayProps) {
  if (!mentalState) {
    return (
      <div className="flex items-center justify-center p-6 bg-gray-100 rounded-lg">
        <Brain className="w-8 h-8 text-gray-400" />
        <p className="ml-2 text-gray-500">Waiting for brain activity data...</p>
      </div>
    );
  }

  // Determine which icon to display based on the mental state
  let ThoughtIcon = Brain;
  let iconColor = "text-blue-500";
  
  if (mentalState.state.toLowerCase() === 'left') {
    ThoughtIcon = ArrowLeft;
    iconColor = "text-green-500";
  } else if (mentalState.state.toLowerCase() === 'right') {
    ThoughtIcon = ArrowRight;
    iconColor = "text-purple-500";
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <ThoughtIcon className={`w-8 h-8 ${iconColor}`} />
          <h2 className="ml-2 text-xl font-semibold">Current Brain Activity</h2>
        </div>
        <span className="px-4 py-1 text-sm font-medium text-white bg-blue-500 rounded-full">
          {(mentalState.confidence * 100).toFixed(1)}% confidence
        </span>
      </div>
      
      <div className="flex items-center">
        <div className="text-3xl font-bold text-gray-800 flex-grow">
          {mentalState.state === 'left' ? 'Thinking Left' : 
           mentalState.state === 'right' ? 'Thinking Right' : 
           `Thinking: ${mentalState.state}`}
        </div>
        
        <div className="w-24 h-24 rounded-full border-4 border-gray-200 relative">
          {mentalState.state.toLowerCase() === 'left' && (
            <div className="absolute inset-0 flex items-center justify-center">
              <ArrowLeft className="w-12 h-12 text-green-500" />
            </div>
          )}
          
          {mentalState.state.toLowerCase() === 'right' && (
            <div className="absolute inset-0 flex items-center justify-center">
              <ArrowRight className="w-12 h-12 text-purple-500" />
            </div>
          )}
          
          {!['left', 'right'].includes(mentalState.state.toLowerCase()) && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Activity className="w-12 h-12 text-blue-500" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}