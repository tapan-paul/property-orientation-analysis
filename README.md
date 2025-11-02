# Property Orientation Analysis

A Python tool that analyzes property locations against road networks to determine house orientations with 97.8% accuracy.

## 🚀 Quick Start

```bash
git clone https://github.com/tapan-paul/property-orientation-analysis.git
cd property-orientation-analysis

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies 
pip3 install -r requirements.txt 

# Download data from Google Drive and place in data/raw/
https://drive.google.com/drive/folders/1rOg2yn6z5Ux9-goPhKoFO_H71PgCKfwd

### If installation fails
# Install system dependencies first (macOS)
brew install proj geos

# Then install packages individually
pip3 install pandas pyarrow geopandas fiona

# Run analysis (uses pre-computed results if geopandas not available)
python3 src/main.py
