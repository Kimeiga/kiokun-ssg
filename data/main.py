# ok i will start from scratch and do it all in one file like we did before so thata I can ensure there won't be an out of memory exception

import json
import os
import gzip
import sys
from collections import defaultdict
from pathlib import Path
import lzma

# Get the directory of the script
script_dir = Path(__file__).resolve().parent
datasets_dir = script_dir / "datasets"

# Add argument parsing
parser = argparse.ArgumentParser(
    description="Process dictionary data with build mode options."
)
parser.add_argument(
    "--build", action="store_true", help="Use SvelteKit build output directory"
)
parser.add_argument(
    "--vercel", action="store_true", help="Use Vercel build output directory"
)
args = parser.parse_args()

# Get the directory of the script
script_dir = Path(__file__).resolve().parent

# Set the output directory based on the arguments
if args.vercel:
    output_dir = script_dir.parent / ".vercel" / "output" / "static" / "dictionary"
elif args.build:
    output_dir = script_dir.parent / ".svelte-kit" / "output" / "client" / "dictionary"
else:
    output_dir = script_dir.parent / "dictionary"

print(f"Output directory: {output_dir}")

print("Loading datasets...")


def load_json_xz(file_path):
    with lzma.open(file_path, "rt", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl_xz(file_path):
    with lzma.open(file_path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def load_dataset(pattern):
    files = list(datasets_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No {pattern} file found in {datasets_dir}")
    file_path = files[0]  # Use the first matching file
    if file_path.suffix == ".xz":
        if "jsonl" in file_path.name:
            return load_jsonl_xz(file_path)
        else:
            return load_json_xz(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


# Load all datasets
jmdict_data = load_dataset("jmdict-*.json*")
jmnedict_data = load_dataset("jmnedict-*.json*")
kanjidic_data = load_dataset("kanjidic2-*.json*")
char_dict_data = load_dataset("dictionary_char_*.jsonl*")
word_dict_data = load_dataset("dictionary_word_*.jsonl*")
# kradfile_data = load_dataset("kradfile-*.json*")
# radkfile_data = load_dataset("radkfile-*.json*")

print("All datasets loaded successfully.")


data = defaultdict(list)
word_index = defaultdict(lambda: defaultdict(list))
jmdict_entries = {}

for index, entry in enumerate(jmdict_data["words"]):
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
                        **(
                            {"a": kana["appliesToKanji"]}
                            if kana["appliesToKanji"] != ["*"]
                            else {}
                        ),
                        **({"r": romkan.to_roma(kana["text"]) if kana["text"] else {}}),
                    }
                    for kana in entry["kana"]
                ]
            }
            if entry["kana"]
            else {}
        ),
        **(
            {
                "s": [
                    {
                        **({"n": sense["antonym"]} if len(sense["antonym"]) else {}),
                        **(
                            {"k": sense["appliesToKana"]}
                            if sense["appliesToKana"] != ["*"]
                            else {}
                        ),
                        **(
                            {"a": sense["appliesToKanji"]}
                            if sense["appliesToKanji"] != ["*"]
                            else {}
                        ),
                        **({"d": sense["dialect"]} if len(sense["dialect"]) else {}),
                        **({"f": sense["field"]} if len(sense["field"]) else {}),
                        "g": (
                            [
                                {
                                    **(
                                        {"g": gloss["gender"]}
                                        if gloss["gender"]
                                        else {}
                                    ),
                                    **({"y": gloss["type"]} if gloss["type"] else {}),
                                    **({"t": gloss["text"]} if gloss["text"] else {}),
                                }
                                for gloss in sense["gloss"]
                            ]
                            if "gloss" in sense
                            else []
                        ),
                        **({"i": sense["info"]} if len(sense["info"]) else {}),
                        **(
                            {"l": sense["languageSource"]}
                            if len(sense["languageSource"])
                            else {}
                        ),
                        **({"m": sense["misc"]} if len(sense["misc"]) else {}),
                        **(
                            {"p": sense["partOfSpeech"]}
                            if len(sense["partOfSpeech"])
                            else {}
                        ),
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
    with open(output_dir / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))

    total_processed += 1

print(f"Total processed entries: {total_processed}")
print(f"Dictionary files have been written to: {output_dir}")
