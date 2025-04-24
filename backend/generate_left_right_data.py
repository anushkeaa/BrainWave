import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def generate_left_right_dataset(filename='mentalstate.csv', num_samples=5000):
    """
    Generate a synthetic dataset for left vs right thinking classification.
    
    Left-thinking patterns typically show stronger activity in the right motor cortex (C4, T8)
    Right-thinking patterns typically show stronger activity in the left motor cortex (C3, T7)
    
    Args:
        filename: Output CSV filename
        num_samples: Number of samples to generate
    """
    print(f"Generating left vs right thinking dataset with {num_samples} samples...")
    
    # Define EEG channels (using standard 10-20 system)
    # We'll use 6 channels that are most relevant for motor imagery
    channel_names = ['F3', 'F4', 'C3', 'C4', 'T7', 'T8']
    
    # Generate timestamps (one per sample)
    timestamps = np.arange(1623456789, 1623456789 + num_samples)
    
    # Initialize data dictionary
    data = {'timestamp': timestamps}
    
    # Generate random base data for each channel
    np.random.seed(42)  # For reproducibility
    for channel in channel_names:
        data[channel] = np.random.normal(0, 5, num_samples)
    
    # Generate labels (alternating blocks of left and right)
    # We'll create blocks of 100 samples to simulate continuous periods of thinking
    labels = []
    for i in range(num_samples):
        if (i // 100) % 2 == 0:
            labels.append('left')
        else:
            labels.append('right')
    
    # Add patterns specific to left/right thinking
    for i in range(num_samples):
        if labels[i] == 'left':
            # Left thinking: stronger mu (8-12 Hz) rhythm suppression in right motor cortex
            # Simulate with increased activity in C4 and T8
            t = i / 250  # Assuming 250 Hz sampling rate
            mu_rhythm = np.sin(2 * np.pi * 10 * t) * 5  # 10 Hz mu rhythm
            data['C4'][i] += mu_rhythm
            data['T8'][i] += mu_rhythm * 0.7
            
            # Add some alpha (8-12 Hz) to F4 too
            data['F4'][i] += np.sin(2 * np.pi * 9 * t) * 2
            
        else:  # Right thinking
            # Right thinking: stronger mu rhythm suppression in left motor cortex
            # Simulate with increased activity in C3 and T7
            t = i / 250  # Assuming 250 Hz sampling rate
            mu_rhythm = np.sin(2 * np.pi * 10 * t) * 5  # 10 Hz mu rhythm
            data['C3'][i] += mu_rhythm
            data['T7'][i] += mu_rhythm * 0.7
            
            # Add some alpha to F3 too
            data['F3'][i] += np.sin(2 * np.pi * 9 * t) * 2
    
    # Add the labels to the data
    data['label'] = labels
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Plot some example data
    plt.figure(figsize=(12, 8))
    
    # Plot one channel for each class
    left_idx = df[df['label'] == 'left'].index[0:250]
    right_idx = df[df['label'] == 'right'].index[0:250]
    
    plt.subplot(2, 1, 1)
    plt.plot(df.loc[left_idx, 'C3'], label='C3 (Left Motor Cortex)')
    plt.plot(df.loc[left_idx, 'C4'], label='C4 (Right Motor Cortex)')
    plt.title('Left Thinking (250 samples)')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(df.loc[right_idx, 'C3'], label='C3 (Left Motor Cortex)')
    plt.plot(df.loc[right_idx, 'C4'], label='C4 (Right Motor Cortex)')
    plt.title('Right Thinking (250 samples)')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('left_right_example.png')
    plt.close()
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Dataset created and saved to {filename}")
    print(f"Example plot saved as 'left_right_example.png'")
    
    return filename

if __name__ == "__main__":
    # Check if dataset already exists
    if os.path.exists('mentalstate.csv'):
        overwrite = input("Dataset 'mentalstate.csv' already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Exiting without creating dataset.")
            exit()
    
    # Create the dataset
    generate_left_right_dataset()
    print("Done! You can now train the model with this dataset.")
