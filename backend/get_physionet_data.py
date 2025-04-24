import os
import urllib.request
import argparse
import tempfile
import zipfile
import shutil
from tqdm import tqdm

def download_physionet_eegmmidb(output_dir, subjects=5, verbose=True):
    """
    Download the PhysioNet EEG Motor Movement/Imagery Dataset.
    
    Args:
        output_dir: Directory to save the downloaded files
        subjects: Number of subjects to download (1-109, or 'all')
        verbose: Print detailed information
    """
    base_url = "https://physionet.org/files/eegmmidb/1.0.0/"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine which subjects to download
    if subjects == 'all':
        subject_ids = range(1, 110)  # Dataset has 109 subjects
    else:
        try:
            num_subjects = int(subjects)
            subject_ids = range(1, min(num_subjects + 1, 110))
        except ValueError:
            print(f"Invalid value for subjects: {subjects}. Using default (5).")
            subject_ids = range(1, 6)
    
    if verbose:
        print(f"Downloading data for {len(list(subject_ids))} subjects...")
    
    # Download the files
    for subject_id in subject_ids:
        subject_str = f"S{subject_id:03d}"
        if verbose:
            print(f"Downloading data for subject {subject_str}...")
        
        # Each subject has multiple runs (tasks)
        for run_id in range(1, 15):  # 14 runs per subject
            run_str = f"R{run_id:02d}"
            filename = f"{subject_str}{run_str}.edf"
            url = f"{base_url}{subject_str}/{filename}"
            
            # Download the file
            try:
                output_path = os.path.join(output_dir, filename)
                if os.path.exists(output_path):
                    if verbose:
                        print(f"  {filename} already exists, skipping")
                    continue
                
                if verbose:
                    print(f"  Downloading {filename}...")
                
                # Create a progress bar for the download
                class DownloadProgressBar(tqdm):
                    def update_to(self, b=1, bsize=1, tsize=None):
                        if tsize is not None:
                            self.total = tsize
                        self.update(b * bsize - self.n)
                
                with DownloadProgressBar(unit='B', unit_scale=True, miniters=1) as t:
                    urllib.request.urlretrieve(
                        url,
                        output_path,
                        reporthook=t.update_to
                    )
            except Exception as e:
                print(f"  Error downloading {filename}: {e}")
    
    if verbose:
        print("Download complete.")
        print(f"Files saved to {output_dir}")
        print(f"Total files downloaded: {len(os.listdir(output_dir))}")
    
    return output_dir

def main():
    parser = argparse.ArgumentParser(description='Download PhysioNet EEG Motor Movement/Imagery Dataset')
    parser.add_argument('--output-dir', default='eegmmidb_data',
                        help='Directory to save the downloaded files')
    parser.add_argument('--subjects', default=5,
                        help='Number of subjects to download (1-109, or "all")')
    parser.add_argument('--convert', action='store_true',
                        help='Convert the downloaded files to our CSV format')
    parser.add_argument('--output-file', default='mentalstate.csv',
                        help='Output CSV file name (when using --convert)')
    parser.add_argument('--task', type=int, default=4,
                        help='Task to extract (4=imagined movement, recommended for BCI)')
    
    args = parser.parse_args()
    
    # Download the data
    download_physionet_eegmmidb(args.output_dir, args.subjects)
    
    # Convert the data if requested
    if args.convert:
        try:
            from convert_eegmmidb import convert_eegmmidb_dataset
            print(f"Converting data from task {args.task} to CSV format...")
            convert_eegmmidb_dataset(
                args.output_dir,
                args.output_file,
                tasks=[args.task]
            )
            print(f"Conversion complete. CSV file saved to {args.output_file}")
        except ImportError:
            print("Error: Could not import convert_eegmmidb module.")
            print("Make sure you have the required dependencies installed:")
            print("  pip install mne pandas numpy")

if __name__ == "__main__":
    main()
