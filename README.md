# Property Orientation Analysis

A Python tool that analyzes property locations against road networks to determine house orientations with 97.8% accuracy.

## 🚀 Quick Start

```bash
git clone https://github.com/tapan-paul/property-orientation-analysis.git
cd property-orientation-analysis

# Install core dependencies
pip3 install pandas pyarrow

# Run analysis (uses pre-computed results if geopandas not available)
python3 src/main.py