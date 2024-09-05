import argparse
import json
from collections import defaultdict
from pathlib import Path
import lzma
import re
import time

import jaconv


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_jsonl(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f]


def load_dataset(pattern, extracted_dir):
    files = list(extracted_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No {pattern} file found in {extracted_dir}")
    file_path = files[0]  # Use the first matching file
    if "jsonl" in file_path.name:
        return load_jsonl(file_path)
    else:
        return load_json(file_path)


def build_japanese_chinese_mapping(char_dict_data):
    japanese_chinese_map = {}

    for char_entry in char_dict_data:
        if "statistics" in char_entry and "top_words" in char_entry["statistics"]:
            top_words = char_entry["statistics"]["top_words"]
            if len(top_words) == 1:
                gloss = top_words[0].get("gloss", "")
                if gloss.startswith("Japanese variant of"):
                    match = re.search(r"of\s+([^\[]+)(?:\[|$)", gloss)
                    if match:
                        chars = match.group(1).split("|")
                        if len(chars) == 2:
                            japanese_chinese_map[char_entry["char"]] = {
                                "t": chars[0],
                                "s": chars[1],
                            }
                        elif len(chars) == 1:
                            japanese_chinese_map[char_entry["char"]] = {
                                "t": chars[0],
                                "s": chars[0],
                            }

    return japanese_chinese_map


parser = argparse.ArgumentParser(
    description="Process dictionary data with extracted files."
)
parser.add_argument(
    "--build", action="store_true", help="Use SvelteKit build output directory"
)
parser.add_argument(
    "--vercel", action="store_true", help="Use Vercel build output directory"
)
args = parser.parse_args()

extracted_dir = Path(__file__).resolve().parent / "datasets" / "extracted"

# Set the output directory based on the arguments
if args.vercel:
    output_dir = (
        Path(__file__).resolve().parent.parent
        / ".vercel"
        / "output"
        / "static"
        / "dictionary"
    )
elif args.build:
    output_dir = (
        Path(__file__).resolve().parent.parent
        / ".svelte-kit"
        / "output"
        / "client"
        / "dictionary"
    )
else:
    output_dir = Path(__file__).resolve().parent.parent / "dictionary"

print(f"Output directory: {output_dir}")

# Load all datasets
jmdict_data = load_dataset("jmdict-*.json", extracted_dir)
jmnedict_data = load_dataset("jmnedict-*.json", extracted_dir)
kanjidic_data = load_dataset("kanjidic2-*.json", extracted_dir)
char_dict_data = load_dataset("dictionary_char_*.jsonl", extracted_dir)
word_dict_data = load_dataset("dictionary_word_*.jsonl", extracted_dir)
jmdict_furigana_data = load_dataset("JmdictFurigana*.json", extracted_dir)
jmnedict_furigana_data = load_dataset("JmnedictFurigana*.json", extracted_dir)

# Add this function call after loading all datasets
japanese_chinese_map = build_japanese_chinese_mapping(char_dict_data)

print("All datasets loaded successfully.")

all_entries = defaultdict(lambda: defaultdict(list))
word_index = defaultdict(lambda: defaultdict(list))


def process_chinese_char_entry(entry, index):
    key = entry["char"]
    all_entries[key]["c_c"].append(entry)


def process_chinese_word_entry(entry, index):
    trad_character = entry["trad"]
    simp_character = entry["simp"]

    all_entries[trad_character]["c_tw"].append(entry)
    if trad_character != simp_character:
        all_entries[simp_character]["c_sw"].append(entry)


def process_kanjidic_entry(entry, index):
    key = entry["literal"]

    minified_entry = {
        "char": entry["literal"],
        "info": {
            **(
                {"frequency": entry["misc"]["frequency"]}
                if entry["misc"]["frequency"]
                else {}
            ),
            **({"grade": entry["misc"]["grade"]} if entry["misc"]["grade"] else {}),
            **(
                {"jlpt_level": entry["misc"]["jlptLevel"]}
                if entry["misc"]["jlptLevel"]
                else {}
            ),
            **(
                {"radical_names": entry["misc"]["radicalNames"]}
                if len(entry["misc"]["radicalNames"])
                else {}
            ),
            "stroke_counts": entry["misc"]["strokeCounts"],
            **(
                {"variants": entry["misc"]["variants"]}
                if len(entry["misc"]["variants"])
                else {}
            ),
        },
        "radicals": [
            {"type": radical["type"], "value": radical["value"]}
            for radical in entry["radicals"]
        ],
        "meanings": {
            "groups": [
                {
                    **(
                        {
                            "meanings": [
                                {**({"value": meaning["value"]} if meaning else {})}
                                for meaning in group["meanings"]
                            ]
                        }
                    ),
                    "readings": [
                        {
                            "type": reading["type"],
                            "value": reading["value"],
                        }
                        for reading in group["readings"]
                    ],
                }
                for group in entry["readingMeaning"]["groups"]
            ],
            **(
                {"nanori": entry["readingMeaning"]["nanori"]}
                if len(entry["readingMeaning"]["nanori"])
                else {}
            ),
        },
    }

    all_entries[key]["c_j"].append(minified_entry)


# Replace the pre-processing step with this:
print("Pre-processing furigana data...")
jmdict_furigana_dict = {}
for item in jmdict_furigana_data:
    jmdict_furigana_dict[item["text"]] = {
        reading: item["furigana"] for reading in item["reading"].split(",")
    }

jmdict_furigana_set = {k: set(v.keys()) for k, v in jmdict_furigana_dict.items()}


# Update the process_jmdict_entry function:
def process_jmdict_entry(entry, index):
    if index % 1000 == 0:
        print(f"Processing JMdict entry {index}")

    keys = []
    kana_dict = {kana["text"]: kana["tags"] for kana in entry.get("kana", [])}
    kana_set = set(kana_dict.keys())

    # Add all kanji and kana representations
    for item in entry.get("kanji", []) + entry.get("kana", []):
        keys.append(item["text"])
        word_index[item["text"]]["j"].append(index)

    # If no keys were found, skip this entry
    if not keys:
        return

    for kanji in entry.get("kanji", []):
        kanji_text = kanji["text"]
        if kanji_text not in jmdict_furigana_set:
            if index % 1000 == 0:
                print(f"  Kanji {kanji_text} not in furigana data")
            kanji["reading"] = [
                {
                    "furigana": [{"ruby": kanji_text, "text": kana}],
                    "tags": kana_dict.get(kana, []),
                    "romaji": jaconv.kata2alphabet(kana),
                }
                for kana in kana_set
            ]
        else:
            if index % 1000 == 0:
                print(f"  Processing furigana for kanji {kanji_text}")
            common_kana = kana_set & jmdict_furigana_set[kanji_text]
            kanji["reading"] = [
                {
                    "furigana": jmdict_furigana_dict[kanji_text][kana],
                    "tags": kana_dict.get(kana, []),
                    "romaji": jaconv.kata2alphabet(kana),
                }
                for kana in common_kana
            ]

    minified_entry = {
        "kanji": [
            {
                "common": kanji.get("common", False),
                "text": kanji["text"],
                "tags": kanji.get("tags", []),
                "reading": kanji.get("reading", []),
            }
            for kanji in entry.get("kanji", [])
        ],
        "reading": [
            {
                "common": kana.get("common", False),
                "text": kana["text"],
                "tags": kana.get("tags", []),
                "applies_to_kanji": (
                    kana["appliesToKanji"] if kana["appliesToKanji"] != ["*"] else []
                ),
                "romaji": jaconv.kata2alphabet(kana["text"]),
            }
            for kana in entry.get("kana", [])
        ],
        "sense": [
            {
                "antonym": sense.get("antonym", []),
                "applies_to_kana": (
                    sense["appliesToKana"] if sense["appliesToKana"] != ["*"] else []
                ),
                "applies_to_kanji": (
                    sense["appliesToKanji"] if sense["appliesToKanji"] != ["*"] else []
                ),
                "dialect": sense.get("dialect", []),
                "field": sense.get("field", []),
                "gloss": [
                    {
                        "gender": gloss.get("gender", ""),
                        "type": gloss.get("type", ""),
                        "text": gloss.get("text", ""),
                    }
                    for gloss in sense.get("gloss", [])
                ],
                "info": sense.get("info", []),
                "language_source": sense.get("languageSource", []),
                "misc": sense.get("misc", []),
                "part_of_speech": sense.get("partOfSpeech", []),
                "related": sense.get("related", []),
            }
            for sense in entry.get("sense", [])
        ],
    }

    # Add the entry to each key
    for key in keys:
        all_entries[key]["w_j"].append(minified_entry)


# Add this to the pre-processing section, after the JMdict furigana processing
print("Pre-processing JMnedict furigana data...")
jmnedict_furigana_dict = {}
for item in jmnedict_furigana_data:
    jmnedict_furigana_dict[item["text"]] = {
        reading: item["furigana"] for reading in item["reading"].split(",")
    }

jmnedict_furigana_set = {k: set(v.keys()) for k, v in jmnedict_furigana_dict.items()}


# Update the process_jmnedict_entry function:
def process_jmnedict_entry(entry, index):
    if index % 1000 == 0:
        print(f"Processing JMnedict entry {index}")

    keys = []
    kana_dict = {kana["text"]: kana["tags"] for kana in entry.get("kana", [])}
    kana_set = set(kana_dict.keys())

    # Add all kanji and kana representations
    for item in entry.get("kanji", []) + entry.get("kana", []):
        keys.append(item["text"])
        word_index[item["text"]]["n"].append(index)

    # If no keys were found, skip this entry
    if not keys:
        return

    for kanji in entry.get("kanji", []):
        kanji_text = kanji["text"]
        if kanji_text not in jmnedict_furigana_set:
            if index % 1000 == 0:
                print(f"  Kanji {kanji_text} not in JMnedict furigana data")
            kanji["reading"] = [
                {
                    "furigana": [{"ruby": kanji_text, "text": kana}],
                    "tags": kana_dict.get(kana, []),
                    "romaji": jaconv.kata2alphabet(kana),
                }
                for kana in kana_set
            ]
        else:
            if index % 1000 == 0:
                print(f"  Processing furigana for kanji {kanji_text}")
            common_kana = kana_set & jmnedict_furigana_set[kanji_text]
            kanji["reading"] = [
                {
                    "furigana": jmnedict_furigana_dict[kanji_text][kana],
                    "tags": kana_dict.get(kana, []),
                    "romaji": jaconv.kata2alphabet(kana),
                }
                for kana in common_kana
            ]

    minified_entry = {
        "reading": (
            [
                {
                    "applies_to_kanji": (
                        kana["appliesToKanji"]
                        if kana["appliesToKanji"] != ["*"]
                        else []
                    ),
                    "tags": kana["tags"],
                    "text": kana["text"],
                    "romaji": jaconv.kata2alphabet(kana["text"]),
                }
                for kana in entry["kana"]
            ]
            if entry.get("kana") and not entry.get("kanji")
            else []
        ),
        "kanji": [
            {
                "tags": kanji.get("tags", []),
                "text": kanji["text"],
                "reading": kanji.get("reading", []),
            }
            for kanji in entry.get("kanji", [])
        ],
        "translation": [
            {
                "related": (
                    list(
                        map(lambda inner: list(map(str, inner)), translation["related"])
                    )
                    if translation.get("related")
                    else []
                ),
                "text": (
                    [t["text"] for t in translation["translation"]]
                    if translation.get("translation")
                    else []
                ),
                "type": translation.get("type", ""),
            }
            for translation in entry.get("translation", [])
        ],
    }

    # Add the entry to each key
    for key in keys:
        all_entries[key]["n_j"].append(minified_entry)


print("Processing Chinese character entries...")
start_time = time.time()
for index, entry in enumerate(char_dict_data):
    if index % 1000 == 0:
        print(f"Processed {index} Chinese character entries")
    process_chinese_char_entry(entry, index)
print(
    f"Processed {len(char_dict_data)} Chinese character entries in {time.time() - start_time:.2f} seconds"
)

print("Processing Chinese word entries...")
start_time = time.time()
for index, entry in enumerate(word_dict_data):
    if index % 1000 == 0:
        print(f"Processed {index} Chinese word entries")
    process_chinese_word_entry(entry, index)
print(
    f"Processed {len(word_dict_data)} Chinese word entries in {time.time() - start_time:.2f} seconds"
)


# Process Kanjidic entries
print("Processing Kanjidic entries...")
start_time = time.time()
for index, entry in enumerate(kanjidic_data["characters"]):
    if index % 1000 == 0:
        print(f"Processed {index} Kanjidic entries")
    process_kanjidic_entry(entry, index)
print(
    f"Processed {len(kanjidic_data['characters'])} Kanjidic entries in {time.time() - start_time:.2f} seconds"
)

# Process JMdict entries
print("Processing JMdict entries...")
start_time = time.time()
for index, entry in enumerate(jmdict_data["words"]):
    if index % 10000 == 0:
        print(f"Processed {index} JMdict entries")
    process_jmdict_entry(entry, index)
print(
    f"Processed {len(jmdict_data['words'])} JMdict entries in {time.time() - start_time:.2f} seconds"
)

# Process JMnedict entries
print("Processing JMnedict entries...")
start_time = time.time()
for index, entry in enumerate(jmnedict_data["words"]):
    if index % 1000 == 0:
        print(f"Processed {index} JMnedict entries")
    process_jmnedict_entry(entry, index)
print(
    f"Processed {len(jmnedict_data['words'])} JMnedict entries in {time.time() - start_time:.2f} seconds"
)

# Add this after processing all entries and before writing JSON files
print("Updating entries with Japanese-Chinese mapping...")
for jp_char, ch_chars in japanese_chinese_map.items():
    # Add c_j to traditional and simplified entries
    if ch_chars["t"] in all_entries:
        all_entries[ch_chars["t"]]["c_j"] = all_entries[ch_chars["t"]].get(
            "c_j", []
        ) + [all_entries[jp_char].get("c_j", [])]
    if ch_chars["s"] in all_entries and ch_chars["s"] != ch_chars["t"]:
        all_entries[ch_chars["s"]]["c_j"] = all_entries[ch_chars["s"]].get(
            "c_j", []
        ) + [all_entries[jp_char].get("c_j", [])]

    # Add c_c to Japanese entry
    if jp_char in all_entries and ch_chars["t"] in all_entries:
        all_entries[jp_char]["c_c"] = all_entries[jp_char].get("c_c", []) + [
            all_entries[ch_chars["t"]].get("c_c", [])
        ]

print(f"Updated {len(japanese_chinese_map)} entries with Japanese-Chinese mapping.")


# Ensure the output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

print("Writing compressed JSON files...")
start_time = time.time()
total_processed = 0

for key, entries_list in all_entries.items():
    if total_processed % 1000 == 0:
        print(f"Wrote {total_processed} compressed JSON files")

    file_path = output_dir / f"{key}.json.gz"
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        json.dump(entries_list, f, ensure_ascii=False, separators=(",", ":"))

    total_processed += 1

print(f"Total processed entries: {total_processed}")
print(f"Compressed dictionary files have been written to: {output_dir}")
print(f"Total writing time: {time.time() - start_time:.2f} seconds")

# Create a manifest file for Vercel's Build Output API
manifest = {
    "version": 2,
    "routes": [{"src": "/dictionary/(.*)", "dest": "/dictionary/$1"}],
    "builds": [{"src": "dictionary/*.json.gz", "use": "@vercel/static"}],
}
with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("Created manifest file for Vercel's Build Output API")
