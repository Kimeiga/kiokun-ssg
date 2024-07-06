import json
import os
import gzip
import sys
from collections import defaultdict
from pathlib import Path

# Get the directory of the script
script_dir = Path(__file__).resolve().parent

# Input and output paths relative to the script location
input_file = script_dir / "jmdict-eng-3.5.0.json.gz"
output_dir = script_dir.parent / "dictionary"

print(f"Reading JMdict file from: {input_file}")
print(f"Output directory: {output_dir}")

data = defaultdict(list)

print("Processing entries...")
with gzip.open(input_file, 'rt', encoding='utf-8') as f:
    jmdict = json.load(f)

for entry in jmdict['words']:
    keys = []

    # Add all kanji representations
    for kanji in entry.get("kanji", []):
        keys.append(kanji["text"])

    # Add all kana representations
    for kana in entry.get("kana", []):
        keys.append(kana["text"])

    # If no keys were found, skip this entry
    if not keys:
        continue

    # Add the entry to each key
    for key in keys:
        data[key].append(entry)

# Ensure the output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

print("Writing JSON files...")
total_processed = 0
for key, entries in data.items():
    with open(output_dir / f'{key}.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, separators=(',', ':'))

    total_processed += 1
    sys.stdout.write(f"\rProcessed: {total_processed} entries")
    sys.stdout.flush()

print(f"\nTotal unique keys processed: {len(data)}")
print("Processing complete.")
