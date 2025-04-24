import type { EEGData, MentalState, EEGChannel } from '../types/eeg';

// Simulated channels
const CHANNELS = ['AF3', 'AF4', 'T7', 'T8', 'PO3', 'PO4'];
const MENTAL_STATES = ['Focused', 'Relaxed', 'Distracted', 'Neutral'];

// Class to generate simulated EEG data
class EEGSimulator {
  private connected: boolean = false;
  private channels: string[] = CHANNELS;
  private currentState: string = 'Neutral';
  private stateTimer: number = 0;
  private stateInterval: number = 5000; // Change mental state every 5 seconds
  
  // Simulate connecting to a device
  connect(): Promise<boolean> {
    return new Promise((resolve) => {
      this.connected = true;
      console.log('Simulated device connected');
      resolve(true);
    });
  }
  
  // Simulate disconnecting from a device
  disconnect(): Promise<boolean> {
    return new Promise((resolve) => {
      this.connected = false;
      console.log('Simulated device disconnected');
      resolve(true);
    });
  }
  
  // Check if connected
  isConnected(): boolean {
    return this.connected;
  }
  
  // Get simulated EEG data
  getEEGData(): Promise<EEGData | null> {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve(null);
        return;
      }
      
      // Update state timer
      this.stateTimer += 100;
      if (this.stateTimer >= this.stateInterval) {
        this.stateTimer = 0;
        this.currentState = MENTAL_STATES[Math.floor(Math.random() * MENTAL_STATES.length)];
      }
      
      // Generate data based on mental state
      const channelData: number[] = this.channels.map((channel, index) => {
        let baseValue = Math.random() * 10;
        
        // Add patterns based on mental state
        switch (this.currentState) {
          case 'Focused':
            if (channel === 'AF3' || channel === 'AF4') {
              baseValue += 15 + Math.sin(Date.now() / 100) * 5;
            }
            break;
          case 'Relaxed':
            if (channel === 'PO3' || channel === 'PO4') {
              baseValue += 10 + Math.sin(Date.now() / 200) * 7;
            }
            break;
          case 'Distracted':
            baseValue += Math.random() * 15;
            break;
          default:
            // Neutral has baseline activity
            baseValue += Math.sin(Date.now() / 300 + index) * 3;
        }
        
        return baseValue;
      });
      
      const eegData: EEGData = {
        timestamp: Date.now(),
        channels: channelData,
        labels: this.channels
      };
      
      resolve(eegData);
    });
  }
  
  // Get simulated mental state
  getMentalState(): Promise<MentalState | null> {
    return new Promise((resolve) => {
      if (!this.connected) {
        resolve(null);
        return;
      }
      
      this.getEEGData().then(eegData => {
        if (!eegData) {
          resolve(null);
          return;
        }
        
        const mentalState: MentalState = {
          state: this.currentState,
          confidence: 0.7 + Math.random() * 0.3, // Random confidence between 0.7-1.0
          eegData: eegData
        };
        
        resolve(mentalState);
      });
    });
  }
  
  // Load data from CSV file (browser-based)
  loadCSV(file: File): Promise<{success: boolean, message: string}> {
    return new Promise((resolve) => {
      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const csv = event.target?.result as string;
          const lines = csv.split('\n');
          
          // Parse header
          const header = lines[0].split(',');
          const channelIndices: number[] = [];
          let labelIndex = -1;
          
          header.forEach((column, index) => {
            const col = column.trim();
            if (col !== 'timestamp' && col !== 'label') {
              channelIndices.push(index);
              this.channels.push(col);
            }
            if (col === 'label') {
              labelIndex = index;
            }
          });
          
          console.log(`Loaded CSV with ${lines.length} rows and ${this.channels.length} channels`);
          
          resolve({
            success: true,
            message: `Successfully loaded dataset with ${lines.length-1} samples and ${this.channels.length} channels`
          });
        } catch (error) {
          console.error('Error parsing CSV:', error);
          resolve({
            success: false,
            message: `Error parsing CSV: ${error}`
          });
        }
      };
      
      reader.onerror = () => {
        resolve({
          success: false,
          message: 'Error reading file'
        });
      };
      
      reader.readAsText(file);
    });
  }
}

// Export a singleton instance
export const eegSimulator = new EEGSimulator();

// API-compatible functions
export async function connectToDevice(): Promise<boolean> {
  return eegSimulator.connect();
}

export async function disconnectFromDevice(): Promise<boolean> {
  return eegSimulator.disconnect();
}

export async function fetchEEGData(): Promise<EEGData | null> {
  return eegSimulator.getEEGData();
}

export async function fetchMentalState(): Promise<MentalState | null> {
  return eegSimulator.getMentalState();
}

export async function checkDatasetStatus(): Promise<{hasDataset: boolean}> {
  return { hasDataset: eegSimulator.isConnected() };
}

export async function trainModel(): Promise<{success: boolean, message: string}> {
  return {
    success: true,
    message: "Simulated model training completed successfully! (Note: This is a frontend-only simulation)"
  };
}
