"""
Adapter for using mental-state.csv dataset with the Brain Activity Monitor
"""
import os
import pandas as pd
import numpy as np
import time
import random
from scipy.signal import savgol_filter

class MentalStateAdapter:
    """Adapter class to use mental-state.csv with our brain activity monitor"""
    
    def __init__(self, csv_path=None):
        """Initialize with path to mental-state.csv"""
        self.using_simulated_data = False
        
        # Find the dataset
        if csv_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
            potential_path = os.path.join(data_dir, "mental-state.csv")
            
            if os.path.exists(potential_path):
                csv_path = potential_path
            else:
                print(f"Could not find mental-state.csv in {data_dir}")
                self.using_simulated_data = True
                return
        
        try:
            self.data = pd.read_csv(csv_path)
            print(f"Loaded mental-state.csv with {len(self.data)} rows")
            
            # Analyze the dataset structure
            self.analyze_columns()
            
            # Set up state variables
            self.current_index = 0
            self.data_length = len(self.data)
            self.left_brain_cols = []
            self.right_brain_cols = []
            self.state_col = None
            self.eye_position_col = None
            self.blink_col = None
            
            # Find relevant columns
            self._identify_columns()
            
            print(f"Dataset ready with {len(self.left_brain_cols)} left brain and {len(self.right_brain_cols)} right brain channels")
            
        except Exception as e:
            print(f"Error loading mental-state.csv: {e}")
            self.using_simulated_data = True
    
    def analyze_columns(self):
        """Analyze columns to identify relevant data"""
        if self.using_simulated_data:
            return
            
        # Print column names
        print("Columns in dataset:")
        for col in self.data.columns:
            print(f"  - {col}")
            
        # Check for missing values
        missing = self.data.isnull().sum()
        if missing.sum() > 0:
            print("Warning: Dataset contains missing values")
            # Fill missing values with forward fill then backward fill
            self.data = self.data.ffill().bfill()
    
    def _identify_columns(self):
        """Identify which columns to use for left/right brain activity"""
        if self.using_simulated_data:
            return
            
        # Common naming patterns for left/right brain activity
        left_patterns = ['left', 'analytical', 'logical', 'fp1', 'f3', 'f7', 't3', 'c3', 'p3', 'o1']
        right_patterns = ['right', 'creative', 'intuitive', 'fp2', 'f4', 'f8', 't4', 'c4', 'p4', 'o2']
        
        # Check for direct state column
        state_patterns = ['state', 'mental_state', 'brain_state', 'activity']
        for col in self.data.columns:
            for pattern in state_patterns:
                if pattern.lower() in col.lower():
                    self.state_col = col
                    break
                    
        # Look for eye position and blink columns
        for col in self.data.columns:
            if any(x in col.lower() for x in ['eye', 'gaze', 'look']):
                self.eye_position_col = col
            if any(x in col.lower() for x in ['blink', 'wink']):
                self.blink_col = col
        
        # Find left/right brain columns
        for col in self.data.columns:
            # Skip non-numeric columns
            if self.data[col].dtype not in [np.float64, np.int64, np.float32, np.int32]:
                continue
                
            # Check if column matches left patterns
            if any(pattern in col.lower() for pattern in left_patterns):
                self.left_brain_cols.append(col)
                
            # Check if column matches right patterns  
            if any(pattern in col.lower() for pattern in right_patterns):
                self.right_brain_cols.append(col)
        
        # If no matches found by name, use the first half of numeric columns for left brain
        # and the second half for right brain
        if not (self.left_brain_cols or self.right_brain_cols):
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
            mid_point = len(numeric_cols) // 2
            
            self.left_brain_cols = numeric_cols[:mid_point]
            self.right_brain_cols = numeric_cols[mid_point:]
            
            print("No clear left/right brain columns identified by name.")
            print(f"Using first {len(self.left_brain_cols)} numeric columns for left brain")
            print(f"Using last {len(self.right_brain_cols)} numeric columns for right brain")
    
    def get_next_reading(self):
        """Get the next reading from the dataset"""
        if self.using_simulated_data:
            return self._generate_simulated_reading()
            
        # Get the current row
        if self.current_index >= self.data_length:
            self.current_index = 0  # loop back to start
            
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        # Calculate left and right brain activity
        left_values = [float(row[col]) for col in self.left_brain_cols if pd.notna(row[col])]
        right_values = [float(row[col]) for col in self.right_brain_cols if pd.notna(row[col])]
        
        # Normalize to 0.1-1.0 range
        left_activity = 0.5  # default
        right_activity = 0.5  # default
        
        if left_values:
            # Normalize using a sigmoid-like transformation
            left_mean = np.mean(left_values)
            left_std = np.std(left_values) if len(left_values) > 1 else 1.0
            left_activity = 0.1 + 0.9 / (1 + np.exp(-left_mean / max(left_std, 0.001)))
            
        if right_values:
            right_mean = np.mean(right_values)
            right_std = np.std(right_values) if len(right_values) > 1 else 1.0
            right_activity = 0.1 + 0.9 / (1 + np.exp(-right_mean / max(right_std, 0.001)))
        
        # Determine brain state
        if self.state_col and self.state_col in row:
            state = str(row[self.state_col]).lower()
            # Map to one of our standard states
            if 'anal' in state or 'logic' in state or 'left' in state:
                state = 'analytical'
            elif 'creat' in state or 'intuit' in state or 'right' in state:
                state = 'creative'
            elif 'balanced' in state or 'neutral' in state:
                state = 'balanced'
            else:
                # Determine based on left/right activity
                if left_activity > right_activity * 1.2:
                    state = 'analytical'
                elif right_activity > left_activity * 1.2:
                    state = 'creative'
                else:
                    state = 'balanced'
        else:
            # Determine based on left/right activity
            if left_activity > right_activity * 1.2:
                state = 'analytical'
            elif right_activity > left_activity * 1.2:
                state = 'creative'
            else:
                state = 'balanced'
        
        # Get eye position and blink info if available
        eye_position = 'center'  # default
        if self.eye_position_col and self.eye_position_col in row:
            position = str(row[self.eye_position_col]).lower()
            if 'left' in position:
                eye_position = 'left'
            elif 'right' in position:
                eye_position = 'right'
            
        blink = False  # default
        if self.blink_col and self.blink_col in row:
            blink_val = row[self.blink_col]
            if isinstance(blink_val, (bool, np.bool_)):
                blink = blink_val
            elif isinstance(blink_val, (int, float, np.number)):
                blink = blink_val > 0.5
            elif isinstance(blink_val, str):
                blink = blink_val.lower() in ['true', 'yes', '1', 't', 'y']
        
        return {
            "left": float(left_activity),
            "right": float(right_activity),
            "state": state,
            "eye_position": eye_position,
            "blink": bool(blink),
            "timestamp": time.time()
        }
    
    def _generate_simulated_reading(self):
        """Generate a simulated EEG reading"""
        t = time.time()
        
        # Generate oscillating values for left and right brain
        left = 0.5 + 0.4 * np.sin(t * 0.2)
        right = 0.5 + 0.4 * np.sin(t * 0.15 + 1.5)  # Out of phase with left
        
        # Determine brain state
        if left > right + 0.2:
            state = 'analytical'
        elif right > left + 0.2:
            state = 'creative'
        else:
            state = 'balanced'
        
        # Random eye position and blink
        eye_position = random.choices(['left', 'center', 'right'], weights=[0.1, 0.8, 0.1])[0]
        blink = random.random() < 0.05  # 5% chance of blink
        
        return {
            "left": left,
            "right": right,
            "state": state,
            "eye_position": eye_position,
            "blink": blink,
            "timestamp": t
        }
    
    def process_webcam_data(self, eye_position, blink_detected):
        """Process webcam data to augment analysis"""
        # Get the next reading
        reading = self.get_next_reading()
        
        # Modify brain activity based on eye position
        if eye_position == "left":
            # Looking left activates right brain
            reading["right"] = min(1.0, reading["right"] * 1.3)
            reading["left"] = max(0.1, reading["left"] * 0.8)
            reading["state"] = "creative"
        elif eye_position == "right":
            # Looking right activates left brain
            reading["left"] = min(1.0, reading["left"] * 1.3)
            reading["right"] = max(0.1, reading["right"] * 0.8)
            reading["state"] = "analytical"
        
        # Update eye position and blink status
        reading["eye_position"] = eye_position
        reading["blink"] = blink_detected
        
        return reading
