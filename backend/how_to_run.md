# How to Run the Brain Activity Monitor with Your Dataset

## Step 1: Verify Your Dataset

Your dataset appears to have a unique format with columns like:
- `lag1_mean_0`, `lag1_mean_1`, etc.
- `lag1_mean_d_h2h1_0`, `lag1_mean_d_h2h1_1`, etc.

This format has been recognized, but it doesn't match the standard EEG format the system expects. We've created a custom adapter for it.

## Step 2: Run the Application

1. Ensure your dataset is in the data directory as `eyegaze.csv`:
   ```
   c:\Users\Jaydeep Mukherjee\Downloads\brainwave\project\src\backend\data\eyegaze.csv
   ```

2. Start the backend server:
   ```
   cd c:\Users\Jaydeep Mukherjee\Downloads\brainwave\project\src\backend
   python standalone.py
   ```

   Look for output mentioning "Successfully initialized custom eyegaze analyzer!"

3. In a separate terminal, start the frontend:
   ```
   cd c:\Users\Jaydeep Mukherjee\Downloads\brainwave\project
   npm start
   ```

## Step 3: Using the Application

1. In the browser interface, click "Connect Brain Device"
2. Click "Turn On Camera" to enable webcam
3. The system will use:
   - Your eyegaze dataset for eye position detection
   - The webcam for supplementary eye tracking
   - Both combined to influence the brain activity visualization

## If You Encounter Problems

If your dataset still isn't recognized correctly:

1. Examine the console output for clues
2. Try renaming some columns in your CSV:
   - Rename the main horizontal eye position column to "gaze_x"
   - Rename the main vertical eye position column to "gaze_y"
   - Save the modified file as `eyegaze.csv`

3. For direct assistance, run the analysis tool:
   ```
   python analyze_dataset.py data\eyegaze.csv
   ```
