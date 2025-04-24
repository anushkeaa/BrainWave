import numpy as np
from scipy import signal
import scipy.fftpack
import matplotlib.pyplot as plt

class EEGProcessor:
    """
    Class for processing EEG signals.
    """
    def __init__(self, sampling_rate=250.0):
        """
        Initialize the EEG processor.
        
        Args:
            sampling_rate: The sampling rate of the EEG data in Hz
        """
        self.sampling_rate = sampling_rate
        self.window_size = int(sampling_rate * 1)  # 1 second window
        self.buffer = []
        
    def bandpass_filter(self, data, lowcut=1.0, highcut=50.0, order=5):
        """
        Apply a bandpass filter to EEG data.
        
        Args:
            data: The EEG data to filter (channels x samples)
            lowcut: The low frequency cutoff in Hz
            highcut: The high frequency cutoff in Hz
            order: The order of the filter
            
        Returns:
            The filtered EEG data
        """
        nyq = 0.5 * self.sampling_rate
        low = lowcut / nyq
        high = highcut / nyq
        
        # Create the bandpass filter
        b, a = signal.butter(order, [low, high], btype='band')
        
        # Apply the filter to each channel
        filtered_data = np.array([signal.filtfilt(b, a, ch) for ch in data])
        
        return filtered_data
    
    def notch_filter(self, data, notch_freq=60.0, quality_factor=30.0):
        """
        Apply a notch filter to remove power line noise.
        
        Args:
            data: The EEG data to filter (channels x samples)
            notch_freq: The frequency to remove in Hz
            quality_factor: The quality factor of the notch filter
            
        Returns:
            The filtered EEG data
        """
        nyq = 0.5 * self.sampling_rate
        notch = notch_freq / nyq
        
        # Create the notch filter
        b, a = signal.iirnotch(notch, quality_factor)
        
        # Apply the filter to each channel
        filtered_data = np.array([signal.filtfilt(b, a, ch) for ch in data])
        
        return filtered_data
    
    def extract_frequency_bands(self, data):
        """
        Extract frequency band powers from EEG data.
        
        Args:
            data: The EEG data (channels x samples)
            
        Returns:
            A dictionary of band powers for each channel
        """
        # Define frequency bands (in Hz)
        bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 50)
        }
        
        # Calculate the FFT for each channel
        fft_data = np.fft.rfft(data, axis=1)
        fft_freqs = np.fft.rfftfreq(data.shape[1], 1.0/self.sampling_rate)
        
        # Calculate band powers
        band_powers = {}
        for band_name, (low, high) in bands.items():
            # Find indices of frequencies in the band
            idx_band = np.logical_and(fft_freqs >= low, fft_freqs <= high)
            
            # Calculate power in the band for each channel
            powers = np.zeros(len(data))
            for i, channel_fft in enumerate(fft_data):
                powers[i] = np.mean(np.abs(channel_fft[idx_band])**2)
            
            band_powers[band_name] = powers
        
        return band_powers
    
    def process_sample(self, sample):
        """
        Process a single EEG sample.
        
        Args:
            sample: Dict containing EEG sample data
            
        Returns:
            Processed sample data
        """
        # Extract raw channel data
        raw_data = np.array(sample['channels'])
        
        # Apply filters
        filtered_data = self.bandpass_filter(raw_data)
        filtered_data = self.notch_filter(filtered_data)
        
        # Update the sample with filtered data
        processed_sample = sample.copy()
        processed_sample['processed_channels'] = filtered_data.tolist()
        
        # Add frequency band information if we have enough data
        self.buffer.append(filtered_data)
        if len(self.buffer) >= self.window_size:
            # Use the most recent window_size samples
            window_data = np.array(self.buffer[-self.window_size:])
            window_data = np.swapaxes(window_data, 0, 1)  # samples->channels x window
            
            # Extract frequency bands
            band_powers = self.extract_frequency_bands(window_data)
            processed_sample['band_powers'] = band_powers
            
            # Keep buffer from growing too large
            if len(self.buffer) > self.window_size * 2:
                self.buffer = self.buffer[-self.window_size:]
        
        return processed_sample
    
    def visualize_bands(self, band_powers, channel_names=None):
        """
        Visualize frequency band powers.
        
        Args:
            band_powers: Dictionary of band powers for each channel
            channel_names: List of channel names
        """
        if not band_powers:
            return
        
        bands = list(band_powers.keys())
        n_channels = len(band_powers[bands[0]])
        
        if channel_names is None:
            channel_names = [f"Channel {i+1}" for i in range(n_channels)]
        
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(n_channels)
        width = 0.15
        multiplier = 0
        
        for band_name in bands:
            offset = width * multiplier
            ax.bar(x + offset, band_powers[band_name], width, label=band_name)
            multiplier += 1
        
        ax.set_xlabel('Channel')
        ax.set_ylabel('Power')
        ax.set_title('EEG Frequency Band Powers')
        ax.set_xticks(x + width * (len(bands) - 1) / 2)
        ax.set_xticklabels(channel_names)
        ax.legend(loc='upper left')
        
        plt.tight_layout()
        plt.savefig('band_powers.png')
        plt.close()

# Example usage
if __name__ == "__main__":
    # Generate some synthetic EEG data
    n_channels = 6
    n_samples = 1000
    sampling_rate = 250.0
    
    # Generate time array
    t = np.arange(n_samples) / sampling_rate
    
    # Generate each channel with different frequency components
    data = np.zeros((n_channels, n_samples))
    for i in range(n_channels):
        # Add sine waves at different frequencies
        data[i] = (
            np.sin(2 * np.pi * 2 * t) +  # 2 Hz (delta)
            0.5 * np.sin(2 * np.pi * 6 * t) +  # 6 Hz (theta)
            2 * np.sin(2 * np.pi * 10 * t) +  # 10 Hz (alpha)
            0.3 * np.sin(2 * np.pi * 20 * t) +  # 20 Hz (beta)
            0.1 * np.sin(2 * np.pi * 40 * t)    # 40 Hz (gamma)
        )
        # Add some noise
        data[i] += np.random.normal(0, 0.5, n_samples)
    
    # Create the processor
    processor = EEGProcessor(sampling_rate=sampling_rate)
    
    # Filter the data
    filtered_data = processor.bandpass_filter(data)
    
    # Extract frequency bands
    band_powers = processor.extract_frequency_bands(filtered_data)
    
    # Visualize the bands
    channel_names = [f"CH{i+1}" for i in range(n_channels)]
    processor.visualize_bands(band_powers, channel_names)
    
    print("Example complete. Band powers visualization saved as 'band_powers.png'")
