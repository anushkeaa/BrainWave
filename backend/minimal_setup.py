import os
import subprocess
import sys

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    return result.returncode == 0

def create_directories():
    """Create necessary directories"""
    print("Creating model directory...")
    os.makedirs("model", exist_ok=True)
    print("Done!")

def install_minimal_dependencies():
    """Install minimal required packages"""
    packages = [
        "flask==2.2.3",
        "flask-cors==3.0.10",
        "numpy==1.23.5",
        "scipy==1.10.1",
        "pandas==1.5.3",
        "scikit-learn==1.2.2",
        "matplotlib==3.7.1"
    ]
    
    print("Installing minimal required packages...")
    for package in packages:
        success = run_command(f"{sys.executable} -m pip install {package}")
        if not success:
            print(f"Failed to install {package}. Trying without version constraint...")
            package_name = package.split("==")[0]
            run_command(f"{sys.executable} -m pip install {package_name}")
    
    print("\nTrying to install TensorFlow (this may take a while)...")
    tf_success = run_command(f"{sys.executable} -m pip install tensorflow==2.11.0")
    if not tf_success:
        print("Failed to install specific TensorFlow version. Trying without version constraint...")
        run_command(f"{sys.executable} -m pip install tensorflow")
    
    print("\nSetup complete! You can now create a sample dataset and train the model.")

def create_venv():
    """Create and activate a virtual environment"""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        run_command("python -m venv venv")
    
    print("\nTo activate the virtual environment, run:")
    if os.name == "nt":  # Windows
        print("venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("source venv/bin/activate")
    
    print("\nAfter activating, run this script again to install dependencies.")

def main():
    # Check if running in virtual environment
    in_venv = sys.prefix != sys.base_prefix
    
    if not in_venv:
        print("You are not running in a virtual environment.")
        create_venv()
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_minimal_dependencies()
    
    print("\nNext steps:")
    print("1. Create sample dataset: python create_sample_dataset.py")
    print("2. Train the model:       python train_model.py")
    print("3. Start the server:      python app.py")

if __name__ == "__main__":
    main()
