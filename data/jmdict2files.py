import json
import os
import gzip
import sys
from collections import defaultdict
from pathlib import Path
import romkan

# Get the directory of the script
script_dir = Path(__file__).resolve().parent

# Input and output paths relative to the script location
input_file = script_dir / "jmdict-eng-3.5.0.json.gz"
output_dir = script_dir.parent / "dictionary"

print(f"Reading JMdict file from: {input_file}")
print(f"Output directory: {output_dir}")

data = defaultdict(list)
word_index = defaultdict(lambda: defaultdict(list))
jmdict_entries = {}

print("Processing entries...")
with gzip.open(input_file, 'rt', encoding='utf-8') as f:
    jmdict = json.load(f)

for index, entry in enumerate(jmdict['words']):
    keys = []

    # Add all kanji representations
    for kanji in entry.get("kanji", []):
        keys.append(kanji["text"])
        word_index[kanji["text"]]["j"].append(index)

    # Add all kana representations
    for kana in entry.get("kana", []):
        keys.append(kana["text"])
        word_index[kana["text"]]["j"].append(index)

    # If no keys were found, skip this entry
    if not keys:
        continue

    # Add the entry to each key
    for key in keys:
        data[key].append(entry)

    # Clean and structure the entry
    jmdict_entries[index] = {
        **(
            {
                "k": [
                    {
                        **({"c": True} if kanji["common"] else {}),
                        **({"t": kanji["text"]} if kanji["text"] else {}),
                        **({"g": kanji["tags"]} if len(kanji["tags"]) else {}),
                    }
                    for kanji in entry["kanji"]
                ]
            }
            if entry["kanji"]
            else {}
        ),
        **(
            {
                "r": [
                    {
                        **({"c": True} if kana["common"] else {}),
                        **({"t": kana["text"]} if kana["text"] else {}),
                        **({"g": kana["tags"]} if len(kana["tags"]) else {}),
                        **({"a": kana["appliesToKanji"]} if kana["appliesToKanji"] != ["*"] else {}),
                        **({"r": romkan.to_roma(kana["text"]) if kana["text"] else {}})
                    }
                    for kana in entry["kana"]
                ]
            }
            if entry["kana"]
            else {}
        ),
        **({
            "s": [
                {
                    **({"n": sense["antonym"]} if len(sense["antonym"]) else {}),
                    **({"k": sense["appliesToKana"]} if sense["appliesToKana"] != ["*"] else {}),
                    **({"a": sense["appliesToKanji"]} if sense["appliesToKanji"] != ["*"] else {}),
                    **({"d": sense["dialect"]} if len(sense["dialect"]) else {}),
                    **({"f": sense["field"]} if len(sense["field"]) else {}),
                    "g": [
                        {
                            **({"g": gloss["gender"]} if gloss["gender"] else {}),
                            **({"y": gloss["type"]} if gloss["type"] else {}),
                            **({"t": gloss["text"]} if gloss["text"] else {}),
                        }
                        for gloss in sense["gloss"]
                    ]
                    if "gloss" in sense else [],
                    ** ({"i": sense["info"]} if len(sense["info"]) else {}),
                    **({"l": sense["languageSource"]} if len(sense["languageSource"]) else {}),
                    **({"m": sense["misc"]} if len(sense["misc"]) else {}),
                    **({"p": sense["partOfSpeech"]} if len(sense["partOfSpeech"]) else {}),
                    **({"r": sense["related"]} if len(sense["related"]) else {}),
                }
                for sense in entry["sense"]
            ]
        }
            if entry["sense"]
            else {}
        ),
    }

# Ensure the output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

print("Writing JSON files...")
total_processed = 0
for key, entries in data.items():
    with open(output_dir / f'{key}.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, separators=(',', ':'))

    total_processed += 1

print(f"Total processed entries: {total_processed}")