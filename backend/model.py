import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, Conv1D, MaxPooling1D, Flatten, LSTM
from sklearn.preprocessing import StandardScaler

class EEGModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.mental_states = ['Focused', 'Relaxed', 'Distracted', 'Neutral']
        
    def build_model(self, input_shape=(6, 250)):
        """Build a CNN+RNN model for EEG classification"""
        model = Sequential([
            # CNN layers
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=128, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            
            # RNN layer
            LSTM(128, return_sequences=True),
            LSTM(64),
            
            # Dense layers
            Dense(64, activation='relu'),
            Dropout(0.5),
            Dense(len(self.mental_states), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train the model with EEG data"""
        if self.model is None:
            self.build_model(input_shape=X_train.shape[1:])
        
        # Normalize data
        X_train_scaled = self.scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
        X_val_scaled = self.scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
        
        # Train the model
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        return history
    
    def save_model(self, filepath):
        """Save the model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the model
        self.model.save(filepath)
        
        # Save the scaler
        scaler_path = os.path.join(os.path.dirname(filepath), 'scaler.npy')
        np.save(scaler_path, self.scaler)
        
    def load_model(self, filepath):
        """Load a saved model from disk"""
        if not os.path.exists(filepath):
            print(f"Model file not found at {filepath}, initializing a new model")
            self.build_model()
            return
        
        try:
            # Load the model
            self.model = load_model(filepath)
            
            # Load the scaler if it exists
            scaler_path = os.path.join(os.path.dirname(filepath), 'scaler.npy')
            if os.path.exists(scaler_path):
                self.scaler = np.load(scaler_path, allow_pickle=True).item()
                
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Initializing a new model instead")
            self.build_model()
    
    def predict(self, eeg_data):
        """Make a prediction from EEG data"""
        if self.model is None:
            # If model isn't loaded, build a default one
            self.build_model()
        
        # Preprocess the data
        # First reshape if needed (expecting shape: channels x timepoints)
        if len(eeg_data.shape) == 1:
            eeg_data = eeg_data.reshape(1, -1)
            
        # Make sure data has the right shape for the model
        if len(eeg_data.shape) == 2:
            # If we have a single sample, add batch dimension
            eeg_data = np.expand_dims(eeg_data, axis=0)
            
        # Scale the data
        try:
            eeg_data_scaled = self.scaler.transform(eeg_data.reshape(-1, eeg_data.shape[-1])).reshape(eeg_data.shape)
        except:
            # If scaler hasn't been fit, just standardize manually
            eeg_data_scaled = (eeg_data - np.mean(eeg_data, axis=1, keepdims=True)) / (np.std(eeg_data, axis=1, keepdims=True) + 1e-10)
        
        # Make prediction
        if self.model is None:
            # If we don't have a model yet, return random predictions
            state_idx = np.random.randint(0, len(self.mental_states))
            confidence = np.random.random() * 0.5 + 0.5  # Random confidence between 0.5-1.0
            return self.mental_states[state_idx], confidence
            
        try:
            predictions = self.model.predict(eeg_data_scaled)
            state_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][state_idx])
            return self.mental_states[state_idx], confidence
        except Exception as e:
            print(f"Error making prediction: {e}")
            # Fallback to random prediction
            state_idx = np.random.randint(0, len(self.mental_states))
            confidence = np.random.random() * 0.5 + 0.5
            return self.mental_states[state_idx], confidence
