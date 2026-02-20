#!/usr/bin/env python3
"""Automated script to fix CasparCG compatibility rules in system_profiles.yaml"""

import re
import sys
from pathlib import Path

def fix_casparcg_rules():
    """Apply the CasparCG compatibility fix to system_profiles.yaml"""
    
    # Find the file
    yaml_file = Path('videowise/system_profiles.yaml')
    
    if not yaml_file.exists():
        print(f"Error: {yaml_file} not found!")
        print("Please run this script from the repository root.")
        sys.exit(1)
    
    # Read the file
    print(f"Reading {yaml_file}...")
    content = yaml_file.read_text()
    
    # Define the old rules pattern (CasparCG section)
    old_pattern = r'(  casparcg:.*?rules:\n)(      - condition: \{codec_contains: "hap"\})'
    
    # Define the replacement with new rule
    replacement = r'\1      # Explicit compatibility for standard supported codecs\n' + \
                  r'      - condition: {codec_in: [h264, prores, dnxhd, dnxhr, mpeg2video, mjpeg]}\n' + \
                  r'        level: compatible\n' + \
                  r'        message: "{codec} is supported by CasparCG Server"\n' + \
                  r'        reason: "CasparCG supports this codec for reliable playback"\n' + \
                  r'      \n' + \
                  r'\2'
    
    # Apply first fix - add new rule
    content = re.sub(old_pattern, replacement, content, flags=re.DOTALL)
    
    # Apply second fix - update incompatibility rule
    content = content.replace(
        'codec_not_in: [h264, prores, dnxhd, dnxhr, hap, notchlc]',
        'codec_not_in: [h264, prores, dnxhd, dnxhr, mpeg2video, mjpeg, hap, notchlc]'
    )
    
    # Write back
    print(f"Writing fixed content to {yaml_file}...")
    yaml_file.write_text(content)
    
    print("✅ Fix applied successfully!")
    print("\nChanges made:")
    print("1. Added explicit codec_in rule for standard codecs")
    print("2. Updated incompatibility rule to include mpeg2video and mjpeg")
    print("\nNext steps:")
    print("  git add videowise/system_profiles.yaml")
    print('  git commit -m "Fix CasparCG compatibility check for standard codecs"')
    print("  git push")

if __name__ == '__main__':
    fix_casparcg_rules()
