import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import type { EEGChannel } from '../types/eeg';

// Register the required Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface EEGVisualizerProps {
  channels: EEGChannel[];
  windowSize: number;
}

export function EEGVisualizer({ channels, windowSize }: EEGVisualizerProps) {
  // Make sure we have valid data to render
  if (!channels || channels.length === 0) {
    return <div className="text-gray-500">No EEG channels available</div>;
  }

  const options = {
    responsive: true,
    animation: false, // Disable animation for better performance
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'EEG Signal Visualization',
      },
    },
  };

  const labels = Array.from({ length: windowSize }, (_, i) => i.toString());
  
  const data = {
    labels,
    datasets: channels.map((channel, index) => ({
      label: channel.name,
      data: channel.data.slice(-windowSize), // Only show the last `windowSize` points
      borderColor: `hsl(${(index * 360) / channels.length}, 70%, 50%)`,
      backgroundColor: `hsla(${(index * 360) / channels.length}, 70%, 50%, 0.5)`,
      borderWidth: 1,
      pointRadius: 0, // Hide points for better performance
    })),
  };

  return (
    <div className="w-full h-[400px]">
      <Line options={options} data={data} />
    </div>
  );
}