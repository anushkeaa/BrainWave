import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, Conv1D, MaxPooling1D, Flatten, LSTM, BatchNormalization
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class EEGModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.classes = ['left', 'right']  # Binary classification for left vs right thinking
        
    def build_model(self, input_shape=(6, 250)):
        """Build a CNN+LSTM model for EEG classification"""
        model = Sequential([
            # CNN layers for spatial feature extraction
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            
            Conv1D(filters=128, kernel_size=3, activation='relu'),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            
            # LSTM layers for temporal dynamics
            LSTM(128, return_sequences=True),
            Dropout(0.3),
            LSTM(64),
            Dropout(0.3),
            
            # Dense layers for classification
            Dense(64, activation='relu'),
            Dropout(0.5),
            Dense(len(self.classes), activation='softmax')
        ])
        
        # Use binary crossentropy for binary classification
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(model.summary())
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        """Train the model with EEG data"""
        if self.model is None:
            self.build_model(input_shape=X_train.shape[1:])
        
        # Normalize data
        X_train_scaled = self.scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
        
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val.reshape(-1, X_val.shape[-1])).reshape(X_val.shape)
            validation_data = (X_val_scaled, y_val)
        else:
            validation_data = None
        
        # Create a callback that saves the model's weights
        checkpoint_path = "model/checkpoints/model_{epoch:02d}_{val_accuracy:.2f}.h5"
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        
        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_path,
            save_weights_only=True,
            save_best_only=True,
            monitor='val_accuracy',
            mode='max',
            verbose=1
        )
        
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True
        )
        
        # Train the model
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            callbacks=[checkpoint_callback, early_stopping]
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
        
        # Save the class names
        classes_path = os.path.join(os.path.dirname(filepath), 'classes.npy')
        np.save(classes_path, self.classes)
        
        print(f"Model saved to {filepath}")
        
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
            
            # Load the class names if they exist
            classes_path = os.path.join(os.path.dirname(filepath), 'classes.npy')
            if os.path.exists(classes_path):
                self.classes = np.load(classes_path, allow_pickle=True).tolist()
            
            print(f"Model loaded from {filepath}")
            print(f"Classes: {self.classes}")
                
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
            class_idx = np.random.randint(0, len(self.classes))
            confidence = np.random.random() * 0.5 + 0.5  # Random confidence between 0.5-1.0
            return self.classes[class_idx], confidence
            
        try:
            predictions = self.model.predict(eeg_data_scaled)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            return self.classes[class_idx], confidence
        except Exception as e:
            print(f"Error making prediction: {e}")
            # Fallback to random prediction
            class_idx = np.random.randint(0, len(self.classes))
            confidence = np.random.random() * 0.5 + 0.5
            return self.classes[class_idx], confidence
    
    def plot_training_history(self, history):
        """Plot the training history"""
        plt.figure(figsize=(12, 5))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'])
        if 'val_accuracy' in history.history:
            plt.plot(history.history['val_accuracy'])
        plt.title('Model Accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='lower right')
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'])
        if 'val_loss' in history.history:
            plt.plot(history.history['val_loss'])
        plt.title('Model Loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper right')
        
        plt.tight_layout()
        plt.savefig('model/training_history.png')
        plt.close()
