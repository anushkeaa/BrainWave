import pandas as pd
import numpy as np
import time
import threading
from queue import Queue

class EEGStreamer:
    """
    Class to simulate streaming EEG data from a CSV file as if it were coming from a real headset.
    """
    def __init__(self, csv_file='mentalstate.csv', speed_factor=1.0):
        """
        Initialize the EEG streamer.
        
        Args:
            csv_file: Path to the CSV file containing EEG data
            speed_factor: How fast to stream the data (1.0 = real-time, 2.0 = twice as fast)
        """
        self.csv_file = csv_file
        self.speed_factor = speed_factor
        self.data = None
        self.channel_names = []
        self.current_idx = 0
        self.running = False
        self.thread = None
        self.data_queue = Queue(maxsize=100)  # Buffer for streaming data
        
    def load_data(self):
        """Load the EEG data from the CSV file."""
        try:
            print(f"Loading data from {self.csv_file}...")
            self.data = pd.read_csv(self.csv_file)
            print(f"Loaded {len(self.data)} samples.")
            
            # Extract channel names (all columns except timestamp and label)
            self.channel_names = [col for col in self.data.columns 
                                 if col not in ['timestamp', 'label']]
            
            print(f"Found {len(self.channel_names)} channels: {self.channel_names}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_next_sample(self):
        """Get the next sample from the data."""
        if self.data is None or self.current_idx >= len(self.data):
            return None
        
        sample = self.data.iloc[self.current_idx]
        self.current_idx += 1
        
        # If we've reached the end, loop back to beginning
        if self.current_idx >= len(self.data):
            print("Reached end of data, looping back to beginning")
            self.current_idx = 0
        
        # Extract channel data and label
        channel_data = [sample[channel] for channel in self.channel_names]
        label = sample['label'] if 'label' in sample else None
        
        return {
            'timestamp': sample['timestamp'] if 'timestamp' in sample else time.time(),
            'channels': channel_data,
            'channel_names': self.channel_names,
            'label': label
        }
    
    def _stream_worker(self):
        """Worker thread that streams data from the CSV file."""
        if not self.load_data():
            print("Failed to load data. Streaming thread exiting.")
            return
        
        print(f"Starting streaming thread. Speed factor: {self.speed_factor}x")
        
        # Calculate sleep time between samples
        # Typically EEG data is sampled at 250Hz, so default sleep is 1/250 seconds
        sleep_time = (1.0 / 250.0) / self.speed_factor
        
        while self.running:
            sample = self.get_next_sample()
            if sample:
                # Add to queue, but don't block if queue is full (just drop the sample)
                try:
                    self.data_queue.put(sample, block=False)
                except:
                    pass  # Queue full, skip this sample
                
                # Sleep to simulate real-time streaming
                time.sleep(sleep_time)
            else:
                # No more samples, exit thread
                self.running = False
    
    def start_streaming(self):
        """Start streaming data from the CSV file."""
        if self.running:
            print("Streaming already in progress")
            return False
        
        self.running = True
        self.current_idx = 0
        self.thread = threading.Thread(target=self._stream_worker)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop_streaming(self):
        """Stop streaming data."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        print("Streaming stopped")
    
    def get_sample(self, block=True, timeout=1.0):
        """
        Get the latest EEG sample.
        
        Args:
            block: Whether to block until a sample is available
            timeout: How long to wait for a sample if blocking
            
        Returns:
            The latest EEG sample or None if no sample is available
        """
        try:
            return self.data_queue.get(block=block, timeout=timeout)
        except:
            return None
    
    def is_streaming(self):
        """Check if streaming is in progress."""
        return self.running

# Example usage
if __name__ == "__main__":
    streamer = EEGStreamer()
    streamer.start_streaming()
    
    try:
        # Print the first 10 samples
        for _ in range(10):
            sample = streamer.get_sample()
            if sample:
                print(f"Sample: {sample['channels'][:3]}... Label: {sample['label']}")
            time.sleep(0.1)
    finally:
        streamer.stop_streaming()
