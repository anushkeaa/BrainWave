import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

export function GraphExplanation() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mt-2">
      <button 
        onClick={() => setIsOpen(prev => !prev)}
        className="flex items-center justify-between w-full"
      >
        <div className="flex items-center">
          <HelpCircle className="w-5 h-5 text-blue-500 mr-2" />
          <span className="font-medium">What do these EEG graph colors mean?</span>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>
      
      {isOpen && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-sm mb-3">
            The graph shows simulated brain wave activity from different brain regions:
          </p>
          
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
              <span className="text-sm">F3: Left Frontal Lobe</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
              <span className="text-sm">F4: Right Frontal Lobe</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
              <span className="text-sm">C3: Left Motor Cortex</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
              <span className="text-sm">C4: Right Motor Cortex</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-purple-500 mr-2"></div>
              <span className="text-sm">P3: Left Parietal Lobe</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-pink-500 mr-2"></div>
              <span className="text-sm">P4: Right Parietal Lobe</span>
            </div>
          </div>
          
          <p className="text-sm">
            <strong>What to look for:</strong> When thinking about moving your left hand, the <span className="text-yellow-600 font-medium">C4 channel</span> (right motor cortex) should show stronger activity. When thinking about moving your right hand, the <span className="text-green-600 font-medium">C3 channel</span> (left motor cortex) should be more active.
          </p>
          
          <div className="mt-3 bg-gray-50 p-2 rounded text-xs text-gray-600">
            <p><strong>Note:</strong> In real EEG systems, the signal would show more complex patterns related to alpha/beta/theta waves at different frequencies.</p>
          </div>
        </div>
      )}
    </div>
  );
}
