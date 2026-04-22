import os

def split_dimension(file_path, output_dir, segment_prefix):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Define the splits based on line numbers (1-indexed converted to 0-indexed)
    # index.md: 1-10 (0:10)
    # reference.md: 11-172 (10:172)
    # L1: 177-349 (176:349)
    # L2: 350-532 (349:532)
    # L3: 533-699 (532:699)
    # L4: 700-860 (699:860)
    # L5: 861-1012 (860:1012)
    # L6: 1013-1157 (1012:1157)
    # L7: 1158-end (1157:)

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.writelines(lines[0:10])
        f.write("\n## Dimension Segments\n")
        f.write("- [L1 · Cold Start](L1-cold-start.md)\n")
        f.write("- [L2 · New Launch](L2-new-launch.md)\n")
        f.write("- [L3 · Growth](L3-growth.md)\n")
        f.write("- [L4 · Mature](L4-mature.md)\n")
        f.write("- [L5 · Decline](L5-decline.md)\n")
        f.write("- [L6 · Phasing Out](L6-phasing-out.md)\n")
        f.write("- [L7 · Inactive](L7-inactive.md)\n")
        f.write("\n[**Technical Reference**](technical-reference.md)\n")

    with open(os.path.join(output_dir, 'technical-reference.md'), 'w', encoding='utf-8') as f:
        f.writelines(lines[10:172])

    segments = [
        ('L1-cold-start.md', 176, 349),
        ('L2-new-launch.md', 349, 532),
        ('L3-growth.md', 532, 699),
        ('L4-mature.md', 699, 860),
        ('L5-decline.md', 860, 1012),
        ('L6-phasing-out.md', 1012, 1157),
        ('L7-inactive.md', 1157, len(lines))
    ]

    for filename, start, end in segments:
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.writelines(lines[start:end])

if __name__ == "__main__":
    split_dimension(
        r'docs/dimensions/01-lifecycle.md',
        r'docs/dimensions/01-lifecycle',
        'L'
    )
