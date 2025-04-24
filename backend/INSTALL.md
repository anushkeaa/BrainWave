# Installation Guide

If you encounter dependency conflicts when installing requirements, follow these alternative installation methods:

## Option 1: Install with pip (one by one)

Installing packages one by one can help identify and resolve conflicts:

```bash
pip install flask==2.2.3
pip install flask-cors==3.0.10
pip install numpy==1.23.5
pip install scipy==1.10.1
pip install pandas==1.5.3
pip install scikit-learn==1.2.2
pip install matplotlib==3.7.1
pip install tensorflow==2.11.0
pip install pylsl==1.16.0
```

## Option 2: Use a virtual environment

Using a virtual environment isolates dependencies and reduces conflicts:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt
```

## Option 3: Use conda (recommended)

Conda has better dependency resolution for scientific packages:

```bash
# Create a conda environment
conda create -n brainwave python=3.9

# Activate the environment
conda activate brainwave

# Install core packages with conda
conda install numpy=1.23.5 scipy pandas=1.5.3 scikit-learn matplotlib

# Install tensorflow with conda
conda install -c conda-forge tensorflow=2.11.0

# Install remaining packages with pip
pip install flask==2.2.3 flask-cors==3.0.10 pylsl==1.16.0
```

## Troubleshooting

If you still encounter dependency issues:

1. Try using Python 3.9 which has better compatibility with TensorFlow
2. If you don't need real hardware support, you can remove `pylsl` from requirements
3. For a minimal setup (just to try the demo), you can use:

```bash
pip install flask flask-cors numpy scipy pandas scikit-learn
```

This will install the packages without version constraints, which may work better on your system, but you might get warnings about TensorFlow requirements.
