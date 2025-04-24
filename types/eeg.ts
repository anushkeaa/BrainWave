/**
 * Type definitions for EEG data
 */

export interface EEGData {
  channels: number[];
  timestamp: number;
  labels?: string[];
}

export interface EEGChannel {
  name: string;
  data: number[];
}

export interface MentalState {
  state: 'analytical' | 'creative' | 'balanced' | 'neutral';
  confidence: number;
  left_brain_activity: number;
  right_brain_activity: number;
  blink_detected: boolean;
  timestamp: number;
}