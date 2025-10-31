# Property Orientation Analysis

A Python tool that analyzes property locations against road networks to determine house orientations with 97.8% accuracy.

## 🚀 Quick Start

```bash
git clone https://github.com/tapan-paul/property-orientation-analysis.git
cd property-orientation-analysis

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install core dependencies
pip3 install pandas pyarrow

# On macOS:
brew install proj geos
pip3 install geopandas

# copy all data into data/raw folder 
https://drive.google.com/drive/folders/1rOg2yn6z5Ux9-goPhKoFO_H71PgCKfwd

# Run analysis (uses pre-computed results if geopandas not available)
python3 src/main.py