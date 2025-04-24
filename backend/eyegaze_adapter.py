"""
Adapter for using eyegaze dataset to provide accurate eye position and state detection
"""
import os
import pandas as pd
import numpy as np
import time
import random
from collections import deque

class EyeGazeAdapter:
    """Adapter class to use eyegaze dataset for tracking eye movements and states"""
    
    def __init__(self, csv_path=None):
        """Initialize with path to eyegaze dataset"""
        self.using_simulated_data = False
        
        # Find the dataset
        if csv_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
            for filename in ["eyegaze.csv", "eye_gaze.csv", "eye-gaze.csv", "eyetracking.csv"]:
                potential_path = os.path.join(data_dir, filename)
                if os.path.exists(potential_path):
                    csv_path = potential_path
                    break
            
            if csv_path is None:
                print(f"Could not find eyegaze dataset in {data_dir}")
                self.using_simulated_data = True
                return
        
        try:
            self.data = pd.read_csv(csv_path)
            print(f"Successfully loaded eyegaze dataset from {csv_path} with {len(self.data)} rows")
            
            # Analyze dataset structure
            self.analyze_columns()
            
            # Set up state variables
            self.current_index = 0
            self.data_length = len(self.data)
            self.eye_position_col = None
            self.gaze_x_col = None
            self.gaze_y_col = None
            self.left_eye_cols = []
            self.right_eye_cols = []
            self.alertness_col = None
            self.blink_col = None
            
            # Recent positions for smoothing
            self.recent_positions = deque(maxlen=3)
            
            # Find relevant columns
            self._identify_columns()
            
            # If we found proper columns, we're using real data
            if (self.eye_position_col or (self.gaze_x_col and self.gaze_y_col) or 
                (self.left_eye_cols and self.right_eye_cols)):
                print("Found valid eye tracking columns - using real eyegaze data")
            else:
                print("Could not identify proper eye tracking columns - using simulated data")
                self.using_simulated_data = True
            
        except Exception as e:
            print(f"Error loading eyegaze dataset: {e}")
            self.using_simulated_data = True
    
    def analyze_columns(self):
        """Analyze columns to identify relevant data"""
        if self.using_simulated_data:
            return
            
        # Print column names
        print("Columns in eyegaze dataset:")
        for col in self.data.columns:
            print(f"  - {col}")
            
        # Check for missing values
        missing = self.data.isnull().sum()
        if missing.sum() > 0:
            print("Warning: Dataset contains missing values - filling them")
            self.data = self.data.ffill().bfill()
    
    def _identify_columns(self):
        """Identify which columns to use for eye tracking data"""
        if self.using_simulated_data:
            return
            
        # Common naming patterns for eye tracking features
        position_patterns = ['position', 'direction', 'looking', 'gaze_dir']
        gaze_x_patterns = ['gaze_x', 'x_coord', 'x_position', 'horizontal']
        gaze_y_patterns = ['gaze_y', 'y_coord', 'y_position', 'vertical']
        left_eye_patterns = ['left_eye', 'lefteye', 'eye_l']
        right_eye_patterns = ['right_eye', 'righteye', 'eye_r']
        alertness_patterns = ['alert', 'awake', 'sleep', 'drowsy']
        blink_patterns = ['blink', 'closed', 'eye_closed']
        
        # Find eye position column (direct categorical value for left/center/right)
        for col in self.data.columns:
            col_lower = col.lower()
            
            # Check for direct position indicator
            if any(pattern in col_lower for pattern in position_patterns):
                # Verify if it contains position values
                unique_values = self.data[col].astype(str).str.lower().unique()
                if any('left' in str(v) for v in unique_values) or any('right' in str(v) for v in unique_values):
                    self.eye_position_col = col
                    print(f"Found eye position column: {col}")
                    break
        
        # Find gaze coordinates (x,y) if no direct position column
        if not self.eye_position_col:
            for col in self.data.columns:
                col_lower = col.lower()
                if any(pattern in col_lower for pattern in gaze_x_patterns):
                    self.gaze_x_col = col
                    print(f"Found gaze X coordinate column: {col}")
                
                if any(pattern in col_lower for pattern in gaze_y_patterns):
                    self.gaze_y_col = col
                    print(f"Found gaze Y coordinate column: {col}")
        
        # Find left/right eye related columns
        for col in self.data.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in left_eye_patterns):
                self.left_eye_cols.append(col)
            
            if any(pattern in col_lower for pattern in right_eye_patterns):
                self.right_eye_cols.append(col)
                
            # Find alertness indicator
            if any(pattern in col_lower for pattern in alertness_patterns):
                self.alertness_col = col
                print(f"Found alertness column: {col}")
                
            # Find blink indicator
            if any(pattern in col_lower for pattern in blink_patterns):
                self.blink_col = col
                print(f"Found blink column: {col}")
        
        # If we found key columns
        if self.left_eye_cols:
            print(f"Found {len(self.left_eye_cols)} left eye columns")
        if self.right_eye_cols:
            print(f"Found {len(self.right_eye_cols)} right eye columns")
            
        # If no specific columns were found, try to guess based on numeric columns
        if not (self.eye_position_col or (self.gaze_x_col and self.gaze_y_col) or self.left_eye_cols or self.right_eye_cols):
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                print("No specific eye tracking columns identified. Using first two numeric columns as X/Y coordinates")
                self.gaze_x_col = numeric_cols[0]
                self.gaze_y_col = numeric_cols[1]
    
    def get_next_reading(self):
        """Get the next eye position reading from the dataset"""
        if self.using_simulated_data:
            return self._generate_simulated_reading()
            
        # Get the current row
        if self.current_index >= self.data_length:
            self.current_index = 0  # loop back to start
            
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        # Determine eye position based on available columns
        eye_position = 'center'  # default
        alertness = 'awake'  # default
        blink_detected = False  # default
        
        # If we have a direct position column
        if self.eye_position_col:
            position_val = str(row[self.eye_position_col]).lower()
            if 'left' in position_val:
                eye_position = 'left'
            elif 'right' in position_val:
                eye_position = 'right'
            elif 'center' in position_val or 'middle' in position_val:
                eye_position = 'center'
                
        # If we have gaze coordinates
        elif self.gaze_x_col and self.gaze_y_col:
            x_val = float(row[self.gaze_x_col])
            
            # Determine left/right based on x coordinate
            # Assuming negative values are left, positive are right, near-zero is center
            if x_val < -0.2:  # threshold for left
                eye_position = 'left'
            elif x_val > 0.2:  # threshold for right
                eye_position = 'right'
            else:
                eye_position = 'center'
                
        # If we have left/right eye columns
        elif self.left_eye_cols and self.right_eye_cols:
            # Get average values for left and right eyes
            left_vals = [float(row[col]) for col in self.left_eye_cols if pd.notna(row[col])]
            right_vals = [float(row[col]) for col in self.right_eye_cols if pd.notna(row[col])]
            
            if left_vals and right_vals:
                left_avg = np.mean(left_vals)
                right_avg = np.mean(right_vals)
                
                # Determine position based on relative values
                if left_avg > right_avg * 1.2:
                    eye_position = 'left'
                elif right_avg > left_avg * 1.2:
                    eye_position = 'right'
                else:
                    eye_position = 'center'
        
        # Check for blink
        if self.blink_col:
            blink_val = row[self.blink_col]
            if isinstance(blink_val, (bool, np.bool_)):
                blink_detected = blink_val
            elif isinstance(blink_val, (int, float, np.number)):
                blink_detected = blink_val > 0.5
            elif isinstance(blink_val, str):
                blink_detected = blink_val.lower() in ['true', 'yes', '1', 't', 'y', 'closed']
        
        # Check for alertness
        if self.alertness_col:
            alertness_val = str(row[self.alertness_col]).lower()
            if any(term in alertness_val for term in ['sleep', 'drowsy', 'tired']):
                alertness = 'sleepy'
        
        # Smooth eye position with recent readings
        self.recent_positions.append(eye_position)
        if len(self.recent_positions) >= 3:
            position_counts = {'left': 0, 'center': 0, 'right': 0}
            for pos in self.recent_positions:
                position_counts[pos] += 1
            eye_position = max(position_counts, key=position_counts.get)
        
        return {
            "eye_position": eye_position,
            "alertness": alertness,
            "blink": blink_detected,
            "timestamp": time.time()
        }
    
    def _generate_simulated_reading(self):
        """Generate a simulated eye gaze reading"""
        t = time.time()
        
        # Slowly oscillate between left, center, and right
        cycle_time = 10  # seconds for a full cycle
        position_index = int((t % cycle_time) / cycle_time * 3)
        positions = ['left', 'center', 'right']
        eye_position = positions[position_index]
        
        # Random blink
        blink_detected = random.random() < 0.05  # 5% chance of blink
        
        # Random alertness
        alertness = random.choices(['awake', 'sleepy'], weights=[0.9, 0.1])[0]
        
        return {
            "eye_position": eye_position,
            "alertness": alertness,
            "blink": blink_detected,
            "timestamp": t
        }
    
    def process_webcam_data(self, webcam_position=None, webcam_blink=None):
        """
        Get eye tracking info, optionally integrating webcam data
        
        Parameters:
        - webcam_position: Eye position from webcam (can override dataset)
        - webcam_blink: Blink detection from webcam (can override dataset)
        
        Returns:
        - Dict with eye position and state info
        """
        # Get reading from dataset
        reading = self.get_next_reading()
        
        # Optionally override with webcam data if provided
        if webcam_position:
            reading["eye_position"] = webcam_position
            
        if webcam_blink is not None:
            reading["blink"] = webcam_blink
        
        return reading
