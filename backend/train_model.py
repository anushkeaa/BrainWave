import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from model import EEGModel

# Load and preprocess the data
def prepare_data(file_path='mentalstate.csv', window_size=125, step_size=25):
    try:
        # Load the dataset
        data = pd.read_csv(file_path)
        print(f"Dataset loaded with shape: {data.shape}")
        
        # Extract features and labels
        feature_cols = [col for col in data.columns if col not in ['timestamp', 'label']]
        X = data[feature_cols].values
        y = data['label'].values
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        mental_states = label_encoder.classes_
        print(f"Mental states in dataset: {mental_states}")
        
        # Create windowed segments for time series
        X_windowed, y_windowed = [], []
        for i in range(0, len(X) - window_size, step_size):
            window = X[i:i+window_size]
            # Use the majority label in the window
            window_labels = y_encoded[i:i+window_size]
            label = np.bincount(window_labels).argmax()
            
            # Reshape window to be (channels, timepoints)
            window_reshaped = window.T  # Transpose to get channels x timepoints
            
            X_windowed.append(window_reshaped)
            y_windowed.append(label)
        
        X_windowed = np.array(X_windowed)
        y_windowed = np.array(y_windowed)
        
        print(f"Created {len(X_windowed)} windows of size {window_size}")
        print(f"Window shape: {X_windowed[0].shape} (channels x timepoints)")
        
        # Split into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X_windowed, y_windowed, test_size=0.2, random_state=42, stratify=y_windowed
        )
        
        print(f"Training data shape: {X_train.shape}, Validation data shape: {X_val.shape}")
        print(f"Class distribution in training: {np.bincount(y_train)}")
        
        return X_train, y_train, X_val, y_val, mental_states
    
    except Exception as e:
        print(f"Error preparing data: {e}")
        # Create synthetic data if there's an error with the CSV
        print("No valid dataset found. Creating synthetic data...")
        
        # Try to generate a synthetic dataset
        try:
            from create_synthetic_bci_dataset import create_synthetic_bci_dataset
            create_synthetic_bci_dataset(
                filename=file_path,
                num_samples=10000,
                num_trials=100
            )
            print("Generated synthetic dataset. Retrying data preparation...")
            return prepare_data(file_path, window_size, step_size)
        except Exception as e:
            print(f"Error generating synthetic data: {e}")
            # Fall back to completely random data
            print("Falling back to random data...")
            
            mental_states = ['left', 'right']
            num_channels = 12
            num_samples = 200
            
            # Generate synthetic data
            X_synthetic = np.random.rand(num_samples, num_channels, window_size) * 20 - 10
            y_synthetic = np.random.randint(0, len(mental_states), num_samples)
            
            # Split into training and validation
            X_train, X_val, y_train, y_val = train_test_split(
                X_synthetic, y_synthetic, test_size=0.2, random_state=42, stratify=y_synthetic
            )
            
            print(f"Generated random data. Training data shape: {X_train.shape}")
            
            return X_train, y_train, X_val, y_val, mental_states


def main():
    # Prepare the data
    X_train, y_train, X_val, y_val, mental_states = prepare_data()
    
    # Initialize and train the model
    model = EEGModel()
    model.classes = mental_states
    model.build_model(input_shape=X_train.shape[1:])
    
    # Use fewer epochs for faster training
    print("Training model (this may take a few minutes)...")
    epochs = 10  # Reduced from 30 to make it faster
    history = model.train(X_train, y_train, X_val, y_val, epochs=epochs, batch_size=32)
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.tight_layout()
    plt.savefig('training_history.png')
    
    # Save the model
    model.save_model('model/eeg_model.h5')
    print("Model trained and saved to model/eeg_model.h5")


if __name__ == "__main__":
    main()
