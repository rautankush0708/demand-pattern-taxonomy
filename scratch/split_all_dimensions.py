import os
import re

def split_all_dimensions():
    dims_dir = 'docs/dimensions'
    files = sorted([f for f in os.listdir(dims_dir) if (f.startswith('0') or f.startswith('1')) and f.endswith('.md')])
    
    nav_updates = {}

    for original_file in files:
        if original_file == 'index.md': continue
        
        # Use technical-reference.md as source since originals were deleted
        file_path = os.path.join(dims_dir, output_folder, 'technical-reference.md')
        if not os.path.exists(file_path):
             continue # Skip if already processed correctly or something
             
        dim_id = output_folder.split('-')[0]
        dim_name = output_folder.split('-')[1].capitalize()
        output_path = os.path.join(dims_dir, output_folder)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Find segment headings
        # Pattern: ## SH1 · Shock Resistant or ## L1 · Cold Start
        segments = []
        part0_end = len(lines)
        
        for i, line in enumerate(lines):
            if line.startswith('## ') and re.search(r'## [A-Z]+[0-9]', line):
                if not segments:
                    part0_end = i
                segments.append((i, line.strip()))
        
        if not segments:
            print(f"No segments found for {output_folder}")
            continue
            
        # Update technical-reference.md (keep only Part 0)
        with open(os.path.join(output_path, 'technical-reference.md'), 'w', encoding='utf-8') as f:
            f.writelines(lines[0:part0_end])
            
        # Split segment files
        index_lines = lines[0:10]
        with open(os.path.join(output_path, 'index.md'), 'w', encoding='utf-8') as f:
            f.writelines(index_lines)
            f.write("\n## Dimension Segments\n")
            for _, title in segments:
                # Create a clean filename from title: "## L1 · Cold Start" -> "L1-cold-start.md"
                clean_name = title.replace('## ', '').replace(' · ', '-').replace(' ', '-').lower() + '.md'
                display_name = title.replace('## ', '')
                f.write(f"- [{display_name}]({clean_name})\n")
            f.write("\n[**Technical Reference**](technical-reference.md)\n")
            
        # Split technical-reference.md
        with open(os.path.join(output_path, 'technical-reference.md'), 'w', encoding='utf-8') as f:
            f.writelines(lines[10:part0_end])
            
        # Split segment files
        nav_segments = []
        for i in range(len(segments)):
            start_line = segments[i][0]
            end_line = segments[i+1][0] if i+1 < len(segments) else len(lines)
            title = segments[i][1]
            
            clean_filename = title.replace('## ', '').replace(' · ', '-').replace(' ', '-').lower() + '.md'
            display_name = title.replace('## ', '')
            
            with open(os.path.join(output_path, clean_filename), 'w', encoding='utf-8') as f:
                f.writelines(lines[start_line:end_line])
            
            nav_segments.append({display_name: f"dimensions/{output_folder}/{clean_filename}"})
            
        nav_updates[original_file] = {
            "Overview": f"dimensions/{output_folder}/index.md",
            "Technical Reference": f"dimensions/{output_folder}/technical-reference.md",
            "Segments": nav_segments
        }
        
    return nav_updates

if __name__ == "__main__":
    updates = split_all_dimensions()
    for key, val in updates.items():
        print(f"--- {key} ---")
        # Print for manual inspection if needed, or I can automate mkdocs.yml update
