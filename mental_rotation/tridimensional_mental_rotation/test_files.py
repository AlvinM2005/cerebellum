#!/usr/bin/env python3
"""
Test script to verify the new file naming convention works
"""
import os
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONDITION_DIR = os.path.join(SCRIPT_DIR, "stimuli", "conditions")

def test_file_loading():
    """Test loading CSV files with new naming convention"""
    
    for VERSION in [1, 2]:
        print(f"\n=== Testing VERSION {VERSION} ===")
        
        for phase in ["demo", "test1", "test2"]:
            # Construct filename using same logic as main.py
            if phase == "demo":
                suffix = f"_{VERSION}"
            else:
                suffix = f"_short_{VERSION}"
            
            filename = f"{phase}{suffix}.csv"
            filepath = os.path.join(CONDITION_DIR, filename)
            
            try:
                with open(filepath, "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                print(f"✅ {filename}: {len(rows)} rows loaded")
                
                # Show first row as example
                if rows:
                    first_row = rows[0]
                    print(f"   Sample: object_id={first_row['object_id']}, "
                          f"condition={first_row['condition']}, "
                          f"key_correct={first_row['key_correct']}")
                    
            except Exception as e:
                print(f"❌ {filename}: Error - {e}")

if __name__ == "__main__":
    test_file_loading()
    print("\n🎉 File naming test completed!")
