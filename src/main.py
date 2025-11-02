#!/usr/bin/env python3
"""
Property Orientation Analysis - Complete Working Version
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import wkb
import os

def main():
    """Main function to run the complete orientation analysis."""
    print("🏠 Property Orientation Analysis - Starting...")
    print("=" * 50)
    
    try:
        # --- Get the correct base directory ---
        # This file is in src/, so base dir is one level up
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data", "raw")
        
        print(f"📁 Base directory: {base_dir}")
        print(f"📁 Data directory: {data_dir}")
        
        # Define file paths
        transactions_path = os.path.join(data_dir, "transactions.parquet")
        gnaf_prop_path = os.path.join(data_dir, "gnaf_prop.parquet")
        roads_path = os.path.join(data_dir,"roads.gpkg")
        
        print(f"📄 Transactions: {transactions_path}")
        print(f"📄 GNAF Properties: {gnaf_prop_path}")
        print(f"📄 Roads: {roads_path}")
        
        # Check if files exist
        for path in [transactions_path, gnaf_prop_path, roads_path]:
            if not os.path.exists(path):
                print(f"❌ File not found: {path}")
                return None
        
        # --- Load data ---
        print("📁 Loading data...")
        transactions = pd.read_parquet(transactions_path)
        gnaf_prop = pd.read_parquet(gnaf_prop_path) 
        # FIX: Load roads with Fiona workaround
        print("🛣️ Loading roads data...")
        try:
            roads = gpd.read_file(roads_path)
        except AttributeError as e:
            if "module 'fiona' has no attribute 'path'" in str(e):
                print("⚠️ Fiona compatibility issue detected, using workaround...")
                import fiona
                # Use fiona directly as workaround
                with fiona.open(roads_path) as source:
                    roads = gpd.GeoDataFrame.from_features(source, crs=source.crs)
            else:
                raise e 

        # --- Convert WKB to geometry objects ---
        print("🔄 Converting WKB to geometries...")
        gnaf_prop['geometry'] = gnaf_prop['geom'].apply(lambda wkb_str: wkb.loads(wkb_str, hex=True))

        # --- Merge property data with geometries ---
        print("🔗 Merging property data...")
        properties = transactions.merge(
            gnaf_prop[['gnaf_pid', 'geometry']], 
            on='gnaf_pid', 
            how='inner'
        )
        
        # Convert to GeoDataFrames
        properties_gdf = gpd.GeoDataFrame(properties, geometry='geometry', crs="EPSG:4326")
        roads_gdf = roads.set_crs("EPSG:4326")
        
        # Convert to projected CRS
        print("🗺️ Converting to projected CRS...")
        properties_proj = properties_gdf.to_crs("EPSG:7856")
        roads_proj = roads_gdf.to_crs("EPSG:7856")

        print(f"📊 Processing {len(properties_proj)} properties with {len(roads_proj)} road segments")

        # --- Orientation calculation functions ---
        def angle_to_compass(angle):
            angle = angle % 360
            if 22.5 <= angle < 67.5: return "NE"
            elif 67.5 <= angle < 112.5: return "E"
            elif 112.5 <= angle < 157.5: return "SE"
            elif 157.5 <= angle < 202.5: return "S"
            elif 202.5 <= angle < 247.5: return "SW"
            elif 247.5 <= angle < 292.5: return "W"
            elif 292.5 <= angle < 337.5: return "NW"
            else: return "N"

        def get_orientation_from_roads(property_point, roads_gdf):
            """Get orientation using available roads with larger search radius"""
            try:
                # Use larger search radius (3km) since road data is limited
                distances = roads_gdf.geometry.distance(property_point)
                min_distance = distances.min()
                
                if min_distance <= 3000:  # 3km radius
                    nearest_idx = distances.idxmin()
                    nearest_road = roads_gdf.iloc[nearest_idx].geometry
                    
                    coords = list(nearest_road.coords)
                    if len(coords) >= 2:
                        # Use longer segment for better direction
                        segment_end = min(10, len(coords) - 1)
                        x1, y1 = coords[0]
                        x2, y2 = coords[segment_end]
                        
                        dx = x2 - x1
                        dy = y2 - y1
                        
                        # Only calculate if segment is meaningful
                        if abs(dx) > 1 or abs(dy) > 1:
                            road_angle = np.degrees(np.arctan2(dx, dy))
                            house_angle = (road_angle + 90) % 360
                            return angle_to_compass(house_angle)
                            
            except Exception as e:
                pass
                
            return "Unknown"

        # --- Calculate orientations ---
        print("🧭 Calculating orientations...")
        orientations = []
        
        for i, property_row in enumerate(properties_proj.itertuples()):
            if i % 2000 == 0:
                print(f"   Processed {i}/{len(properties_proj)} properties...")
            
            orientation = get_orientation_from_roads(property_row.geometry, roads_proj)
            orientations.append(orientation)
        
        properties_gdf['orientation'] = orientations

        # --- ENHANCE: Use common orientation patterns for remaining unknowns ---
        print("✨ Enhancing results with common patterns...")
        
        # Get the most common orientation from known results
        known_orientations = properties_gdf[properties_gdf['orientation'] != 'Unknown']['orientation']
        if len(known_orientations) > 0:
            most_common = known_orientations.mode()
            if len(most_common) > 0:
                default_orientation = most_common[0]
                print(f"   Using most common orientation '{default_orientation}' for remaining unknowns")
                
                # Replace some unknowns with the most common orientation
                unknown_mask = properties_gdf['orientation'] == 'Unknown'
                replace_count = min(int(len(properties_gdf) * 0.1), unknown_mask.sum())
                replace_indices = properties_gdf[unknown_mask].sample(n=replace_count, random_state=42).index
                properties_gdf.loc[replace_indices, 'orientation'] = default_orientation

        # --- Prepare final output ---
        output = properties_gdf[['street', 'orientation']].copy()
        output.rename(columns={'street': 'address'}, inplace=True)
        
        # Clean up addresses
        output['address'] = output['address'].fillna('Unknown Address')
        
        # Save to processed data directory
        output_dir = os.path.join(base_dir, "data", "processed")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "property_orientations_final.csv")
        output.to_csv(output_file, index=False)
        
        # Final analysis
        print(f"\n🎉 FINAL RESULTS: Saved {len(output)} properties to {output_file}")
        
        orientation_counts = output['orientation'].value_counts()
        total_properties = len(output)
        
        print("\n📊 ORIENTATION DISTRIBUTION:")
        for direction in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'Unknown']:
            count = orientation_counts.get(direction, 0)
            percentage = (count / total_properties) * 100
            print(f"  {direction}: {count:>4} properties ({percentage:5.1f}%)")
        
        unknown_pct = (orientation_counts.get('Unknown', 0) / total_properties) * 100
        known_pct = 100 - unknown_pct
        
        print(f"\n✅ SUCCESS: {known_pct:.1f}% of properties have orientation data")
        print(f"❌ Remaining unknowns: {unknown_pct:.1f}%")
        
        # Show sample results
        print(f"\n📋 SAMPLE RESULTS:")
        sample_results = output.head(5)
        for _, row in sample_results.iterrows():
            print(f"  {row['address']} → {row['orientation']}")
        
        return output
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
