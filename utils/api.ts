/**
 * API utilities for connecting to the BCI backend
 */

import type { EEGData, MentalState } from '../types/eeg';

const API_BASE_URL = 'http://localhost:5000/api';

// Ping the backend to check if it's running
export const checkBackendStatus = async (): Promise<{ hasDataset: boolean }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/dataset_status`);
    
    if (!response.ok) {
      throw new Error('Failed to check dataset status');
    }
    
    const data = await response.json();
    return { hasDataset: data.hasDataset };
  } catch (error) {
    console.error('Error checking dataset status:', error);
    return { hasDataset: false };
  }
};

// Connect to the EEG device (or simulator)
export const connectToDevice = async (useWebcam: boolean = false, startImmediately: boolean = true): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/connect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ use_webcam: useWebcam, start_immediately: startImmediately }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to connect to device');
    }
    
    return true;
  } catch (error) {
    console.error('Error connecting to device:', error);
    throw error;
  }
};

// Disconnect from the EEG device
export const disconnectFromDevice = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/disconnect`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to disconnect from device');
    }
    
    return true;
  } catch (error) {
    console.error('Error disconnecting from device:', error);
    throw error;
  }
};

// Fetch the latest EEG data
export const fetchEEGData = async (): Promise<EEGData | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/eeg`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch EEG data');
    }
    
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error fetching EEG data:', error);
    return null;
  }
};

// Fetch the latest mental state
export const fetchMentalState = async (): Promise<MentalState | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/mental_state`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch mental state');
    }
    
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error fetching mental state:', error);
    return null;
  }
};

// Emergency function to bypass normal connection process
export const bypassConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bypass`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to bypass connection');
    }
    
    return true;
  } catch (error) {
    console.error('Error bypassing connection:', error);
    return false;
  }
};

// Start the mock data generator
export const startMockDataGenerator = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/start_mock`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to start mock data generator');
    }
    
    return true;
  } catch (error) {
    console.error('Error starting mock data generator:', error);
    return false;
  }
};

// Stop the mock data generator
export const stopMockDataGenerator = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/stop_mock`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to stop mock data generator');
    }
    
    return true;
  } catch (error) {
    console.error('Error stopping mock data generator:', error);
    return false;
  }
};
