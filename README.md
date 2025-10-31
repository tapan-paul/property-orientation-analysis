# Property Orientation Analysis

A Python tool to determine house orientations (compass directions) using geospatial data and road networks.

## 🎯 Project Overview

This project analyzes property data to determine which direction each house faces (N, NE, E, SE, S, SW, W, NW) using:
- Property transaction data with addresses
- Geocoded property locations (GNAF data)
- OpenStreetMap road network data

## 📊 Results

- **Success Rate**: 97.8% of properties analyzed
- **Total Properties**: 20,801
- **Most Common Orientation**: South (53.9%)
- **Unknown Rate**: Only 2.2%

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/tapan-paul/property-orientation-analysis.git
cd property-orientation-analysis

# Install dependencies
pip3 install -r requirements.txt

# Run analysis
python src/main.py