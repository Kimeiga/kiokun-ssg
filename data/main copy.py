import os
import json
import shutil
from pathlib import Path
from jp.process_japanese import process_japanese_data
# Assuming you'll create a similar module for Chinese
# from cn.process_chinese import process_chinese_data

# Get the project root directory
project_root = Path(__file__).parents[1]

# Define paths
databases_dir = project_root / 'databases'
dictionary_dir = project_root / 'dictionary'

def atomic_write_dictionary(data):
    """
    Atomically write data to the dictionary directory.
    If the directory exists, it's deleted and recreated.
    """
    if dictionary_dir.exists():
        shutil.rmtree(dictionary_dir)
    
    dictionary_dir.mkdir(parents=True)
    
    for key, content in data.items():
        with open(dictionary_dir / f'{key}.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

def main():
    # Process Japanese data
    print("Processing Japanese data...")
    jmdict_path = databases_dir / 'jmdict-eng-3.5.0.json.gz'
    jp_output = process_japanese_data(jmdict_path)

    # Process Chinese data (placeholder for future implementation)
    # print("Processing Chinese data...")
    # cn_output = process_chinese_data(...)

    # Combine outputs (extend this when adding Chinese data)
    all_output = jp_output  # Merge with cn_output when implemented

    # Atomically write outputs to dictionary files
    print("Writing output to dictionary files...")
    atomic_write_dictionary(all_output)

    print("Processing complete. Dictionary files have been updated.")

if __name__ == "__main__":
    main()