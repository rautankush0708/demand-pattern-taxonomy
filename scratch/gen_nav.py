import os
import re

def generate_nav_yaml():
    dims_dir = 'docs/dimensions'
    folders = sorted([f for f in os.listdir(dims_dir) if os.path.isdir(os.path.join(dims_dir, f))])
    
    print("  - Dimensions:")
    print("    - Overview: dimensions/index.md")
    
    for folder in folders:
        # folder name: 01-lifecycle
        dim_id = folder.split('-')[0]
        dim_name = folder.split('-')[1].capitalize()
        
        # Display name: "01 · Lifecycle"
        display_name = f"{dim_id} · {dim_name}"
        
        print(f"    - {display_name}:")
        print(f"      - Overview: dimensions/{folder}/index.md")
        print(f"      - Technical Reference: dimensions/{folder}/technical-reference.md")
        
        # Get segments
        files = sorted(os.listdir(os.path.join(dims_dir, folder)))
        segments = [f for f in files if f not in ['index.md', 'technical-reference.md']]
        
        if segments:
            print(f"      - Segments:")
            for seg in segments:
                # filename: l1-cold-start.md
                # Title: L1 · Cold Start
                parts = seg.replace('.md', '').split('-')
                seg_id = parts[0].upper()
                seg_name = " ".join(parts[1:]).capitalize()
                seg_display = f"{seg_id} · {seg_name}"
                
                print(f"        - {seg_display}: dimensions/{folder}/{seg}")

if __name__ == "__main__":
    generate_nav_yaml()
