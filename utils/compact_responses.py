"""
One-time migration script to remove empty lines from response files and update mappings.

This script:
1. Removes all empty/whitespace-only lines from 9 txt files
2. Builds old-to-new line number mappings
3. Updates all Doc B Position references in corresponding md mapping files
4. Verifies correctness before writing any files
"""

import re
import os

# ANSI color code pattern
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

# Mapping of script numbers to their file names
PAIRS = [
    ('01', '01_basic_qa.py'),
    ('02', '02_chain_of_thought.py'),
    ('03', '03_multi_hop_qa.py'),
    ('04', '04_reasoning_agents.py'),
    ('05', '05_structured_output.py'),
    ('08', '08_few_shot_examples.py'),
    ('09', '09_bootstrap_optimizer.py'),
    ('14', '14_optimizer.py'),
    ('15', '15_mapping.py'),
]


def is_empty_line(line):
    """Check if a line is empty after stripping ANSI codes and whitespace."""
    stripped = ANSI_ESCAPE.sub('', line).strip()
    return stripped == ''


def build_old_to_new_mapping(original_lines):
    """Build mapping from old line numbers (1-indexed) to new line numbers (1-indexed)."""
    old_to_new = {}
    new_idx = 0
    
    for old_idx, line in enumerate(original_lines, start=1):
        if not is_empty_line(line):
            new_idx += 1
            old_to_new[old_idx] = new_idx
        else:
            old_to_new[old_idx] = None
    
    return old_to_new


def compact_lines(original_lines):
    """Remove empty lines from original content."""
    return [line for line in original_lines if not is_empty_line(line)]


def remap_token(token, old_to_new):
    """Remap a single position token (e.g., '23:9' or '0:0')."""
    if ':' not in token:
        return token
    
    line_str, col_str = token.split(':', 1)
    try:
        line_n = int(line_str)
    except ValueError:
        return token
    
    if line_n == 0:  # Sentinel value
        return token
    
    new_line = old_to_new.get(line_n)
    if new_line is None:
        raise ValueError(f"Line {line_n} was removed, cannot remap position")
    
    return f"{new_line}:{col_str}"


def remap_doc_b_position(pos_str, old_to_new):
    """
    Remap Doc B Position cell which can be in one of three formats:
    1. Range: '42:1-43:74'
    2. Multi-comma: '10:5, 15:7, 28:7'
    3. Single: '23:9'
    """
    pos_str = pos_str.strip()
    
    # Check for range format (e.g., '42:1-43:74')
    range_match = re.match(r'^(\d+:\d+)-(\d+:\d+)$', pos_str)
    if range_match:
        start_token = range_match.group(1)
        end_token = range_match.group(2)
        new_start = remap_token(start_token, old_to_new)
        new_end = remap_token(end_token, old_to_new)
        return f"{new_start}-{new_end}"
    
    # Check for multi-comma format (e.g., '10:5, 15:7, 28:7')
    if ',' in pos_str:
        tokens = [t.strip() for t in pos_str.split(',')]
        remapped = [remap_token(t, old_to_new) for t in tokens]
        return ', '.join(remapped)
    
    # Single token format (e.g., '23:9')
    return remap_token(pos_str, old_to_new)


def extract_string_at_position(lines, line_n, col_n, length):
    """Extract a string from lines at given position (1-indexed line, 0-indexed col)."""
    if line_n < 1 or line_n > len(lines):
        return None
    
    line = lines[line_n - 1]
    # Strip ANSI codes for comparison
    line_clean = ANSI_ESCAPE.sub('', line)
    
    if col_n + length > len(line_clean):
        return None
    
    return line_clean[col_n:col_n + length]


def parse_position_token(token):
    """Parse position token into (line, col) tuple."""
    parts = token.split(':')
    if len(parts) != 2:
        return None
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        return None


def verify_mapping(old_lines, new_lines, old_to_new, mappings):
    """
    Verify that remapping is correct by checking that strings at old positions
    match strings at new positions.
    """
    for doc_a_pos, doc_a_len, doc_b_pos_str, doc_b_len_str, label, description in mappings:
        # Parse Doc B Position string and lengths
        # Could be range, multi-comma, or single format
        try:
            # Extract position tokens from doc_b_pos_str
            if '-' in doc_b_pos_str and ',' not in doc_b_pos_str:
                # Range format
                tokens = re.findall(r'\d+:\d+', doc_b_pos_str)
            elif ',' in doc_b_pos_str:
                # Multi-comma format
                tokens = [t.strip() for t in doc_b_pos_str.split(',')]
            else:
                # Single format
                tokens = [doc_b_pos_str]
            
            # Parse lengths
            if ',' in doc_b_len_str:
                lengths = [int(l.strip()) for l in doc_b_len_str.split(',')]
            else:
                lengths = [int(doc_b_len_str)]
            
            # Verify each position
            for token, length in zip(tokens, lengths):
                token = token.strip()
                parsed = parse_position_token(token)
                if parsed is None:
                    continue
                
                old_line, col = parsed
                
                # Skip sentinel value
                if old_line == 0:
                    continue
                
                # Check if line exists in original
                if old_line > len(old_lines):
                    raise ValueError(f"Old line {old_line} out of range")
                
                # Extract string at old position
                old_str = extract_string_at_position(old_lines, old_line, col, length)
                if old_str is None:
                    raise ValueError(
                        f"Could not extract {length} chars at {old_line}:{col} "
                        f"from {label}"
                    )
                
                # Get new line number
                new_line = old_to_new.get(old_line)
                if new_line is None:
                    raise ValueError(f"Line {old_line} was removed, cannot verify")
                
                # Extract string at new position in compacted lines
                new_str = extract_string_at_position(new_lines, new_line, col, length)
                if new_str is None:
                    raise ValueError(
                        f"Could not extract {length} chars at new {new_line}:{col} "
                        f"from compacted lines for {label}"
                    )
                
                # Compare
                if old_str != new_str:
                    raise ValueError(
                        f"Mismatch for {label}: "
                        f"old[{old_line}:{col}]={repr(old_str)} vs "
                        f"new[{new_line}:{col}]={repr(new_str)}"
                    )
        
        except Exception as e:
            print(f"Verification error: {e}")
            raise


def update_mapping_file(md_path, old_to_new):
    """Update Doc B Position references in mapping file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_lines = []
    mappings = []  # For verification
    
    for i, line in enumerate(lines):
        # Check for special CSV line format (line 7 in 08_mapping.md)
        if ',' in line and ':' in line and '|' not in line and line.strip():
            # This is the special CSV line format
            parts = line.rstrip('\n').split(',')
            
            # Doc B Position is at comma-index 3
            if len(parts) > 3:
                doc_b_pos = parts[3].strip()
                try:
                    remapped = remap_doc_b_position(doc_b_pos, old_to_new)
                    parts[3] = f" {remapped} "
                except Exception as e:
                    print(f"Error remapping CSV line in {md_path}: {e}")
                    raise
            
            updated_lines.append(','.join(parts) + '\n')
        
        # Check for table row
        elif '|' in line and i > 1:  # Skip header and separator rows
            cells = line.split('|')
            
            # Check if this is a separator row
            if len(cells) > 2 and all(c.strip().replace('-', '').strip() == '' for c in cells[1:]):
                updated_lines.append(line)
                continue
            
            # Check if this is the header row
            if 'Doc A' in cells[1] if len(cells) > 1 else False:
                updated_lines.append(line)
                continue
            
            # This is a data row
            if len(cells) >= 5:
                doc_a_pos = cells[1].strip() if len(cells) > 1 else ''
                doc_a_len = cells[2].strip() if len(cells) > 2 else ''
                doc_b_pos = cells[3].strip() if len(cells) > 3 else ''
                doc_b_len = cells[4].strip() if len(cells) > 4 else ''
                
                # Store for verification
                label = cells[5].strip() if len(cells) > 5 else ''
                description = cells[6].strip() if len(cells) > 6 else ''
                mappings.append((doc_a_pos, doc_a_len, doc_b_pos, doc_b_len, label, description))
                
                # Remap Doc B Position (cell index 3)
                try:
                    remapped = remap_doc_b_position(doc_b_pos, old_to_new)
                    cells[3] = f" {remapped} "
                except Exception as e:
                    print(f"Error remapping in {md_path}: {e}")
                    raise
            
            updated_lines.append('|'.join(cells))
        else:
            updated_lines.append(line)
    
    return ''.join(updated_lines), mappings


def main():
    """Main migration function."""
    print("Starting migration to remove empty lines from responses...")
    
    for num, script_name in PAIRS:
        txt_path = f"responses/{num}_prompt+response.txt"
        md_path = f"responses/{num}_mapping.md"
        
        print(f"\nProcessing {num}...")
        
        # Skip if txt doesn't exist (not yet created)
        if not os.path.exists(txt_path):
            print(f"  {txt_path} does not exist yet, skipping")
            continue
        
        # Read original txt file
        with open(txt_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        print(f"  Original: {len(original_lines)} lines")
        
        # Build mapping
        old_to_new = build_old_to_new_mapping(original_lines)
        
        # Compact lines
        compacted_lines = compact_lines(original_lines)
        
        print(f"  Compacted: {len(compacted_lines)} lines (removed {len(original_lines) - len(compacted_lines)})")
        
        # Read and update mapping file
        if os.path.exists(md_path):
            print(f"  Updating {md_path}...")
            updated_md, mappings = update_mapping_file(md_path, old_to_new)
            
            # Verify mapping
            try:
                verify_mapping(original_lines, compacted_lines, old_to_new, mappings)
                print(f"  Verification passed for {num}")
            except Exception as e:
                print(f"  ERROR: Verification failed for {num}: {e}")
                print(f"  Aborting migration to avoid data corruption")
                return False
            
            # Write updated mapping file
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(updated_md)
            print(f"  Updated {md_path}")
        
        # Write compacted txt file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.writelines(compacted_lines)
        print(f"  Updated {txt_path}")
    
    print("\n✓ Migration complete!")
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
