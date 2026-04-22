import os
import re

def fix_split_all_dimensions():
    dims_dir = 'docs/dimensions'
    folders = sorted([f for f in os.listdir(dims_dir) if os.path.isdir(os.path.join(dims_dir, f))])
    
    for folder in folders:
        ref_path = os.path.join(dims_dir, folder, 'technical-reference.md')
        if not os.path.exists(ref_path):
            continue
            
        with open(ref_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Find segment headings
        # Pattern: ## [A-Z]+[0-9]
        segments = []
        part0_end = len(lines)
        
        for i, line in enumerate(lines):
            if line.startswith('## ') and re.search(r'## [A-Z]+[0-9]', line):
                if not segments:
                    part0_end = i
                segments.append((i, line.strip()))
        
        if not segments:
            print(f"No segments found in {folder}/technical-reference.md")
            continue
            
        print(f"Splitting {len(segments)} segments in {folder}...")
        
        # Update technical-reference.md (keep only Part 0)
        # Note: the lines already start from line 11 of original file
        with open(ref_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[0:part0_end])
            
        # Split segment files
        index_path = os.path.join(dims_dir, folder, 'index.md')
        with open(index_path, 'r', encoding='utf-8') as f:
            index_lines = f.readlines()
            
        # Update index.md with segment links
        # We find the "## Dimension Segments" line
        new_index_lines = []
        for line in index_lines:
            new_index_lines.append(line)
            if line.strip() == "## Dimension Segments":
                break
        
        for i in range(len(segments)):
            start_line = segments[i][0]
            end_line = segments[i+1][0] if i+1 < len(segments) else len(lines)
            title = segments[i][1]
            
            # Clean filename: "## SH1 · Shock Resistant" -> "sh1-shock-resistant.md"
            clean_filename = title.replace('## ', '').replace(' · ', '-').replace(' ', '-').lower() + '.md'
            display_name = title.replace('## ', '')
            
            segment_path = os.path.join(dims_dir, folder, clean_filename)
            with open(segment_path, 'w', encoding='utf-8') as f:
                f.writelines(lines[start_line:end_line])
            
            new_index_lines.append(f"- [{display_name}]({clean_filename})\n")
            
        new_index_lines.append("\n[**Technical Reference**](technical-reference.md)\n")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.writelines(new_index_lines)

if __name__ == "__main__":
    fix_split_all_dimensions()
