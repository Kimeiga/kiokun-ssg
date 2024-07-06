import json
import os
from collections import defaultdict
import sys

# Output directory relative to the script location
output_dir = "../static"

print("Reading JMdict file...")
with open("jmdict-eng-3.5.0.json", 'r', encoding='utf-8') as f:
    jmdict = json.load(f)

data = defaultdict(list)

print("Processing entries...")
for entry in jmdict['words']:
    key = ""
    if entry["kanji"]:
        key = entry["kanji"][0]["text"]
    elif entry["kana"]:
        key = entry["kana"][0]["text"]

    if key:
        data[key].append(entry)

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

print("Writing JSON files...")
total_processed = 0
for key, entries in data.items():
    with open(os.path.join(output_dir, f'{key}.json'), 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, separators=(',', ':'))

    total_processed += 1
    sys.stdout.write(f"\rProcessed: {total_processed} entries")
    sys.stdout.flush()

print(f"\nTotal unique keys processed: {len(data)}")
print("Processing complete.")
