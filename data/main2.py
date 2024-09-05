import json
import os
import gzip
import sys
from collections import defaultdict
from pathlib import Path
import romkan
import itertools

from data.jp.jmdict import load_jmdict, JMdictEntry
from data.jp.kanjidic import load_kanjidic, Kanjidic2Character
from data.jp.jmnedict import load_jmnedict, JMnedictWord
from data.zh.char_dict import load_chinese_char_dict, ChineseCharEntry
from data.zh.word_dict import load_chinese_word_dict, ChineseWordEntry

# Load j2ch mapping and exceptions
with open("data/j2ch/j2ch.json", "r", encoding="utf-8") as file:
    j2ch = json.load(file)

# Load Japanese variants mapping
with open(
    "data/zh/char_dict/japanese_variants_mapping.json", "r", encoding="utf-8"
) as file:
    japanese_variants_map = json.load(file)

j_exceptions = {
    # ... (keep your existing exceptions)
}


def j2ch_get(j):
    return j2ch.get(j, j)


def generate_combinations2(key):
    return ["".join(j2ch_get(char) for char in key)]


def filter_entries(combinations, index):
    return [comb for comb in combinations if comb in index]


def get_j2ch_word(key, index):
    if key in j_exceptions:
        return [j_exceptions[key]]
    combinations = generate_combinations2(key)
    return filter_entries(combinations, index)


# Get the directory of the script
script_dir = Path(__file__).resolve().parent
output_dir = script_dir.parent / "dictionary"

print(f"Output directory: {output_dir}")

data = defaultdict(lambda: defaultdict(list))
word_index = defaultdict(lambda: defaultdict(list))
jmdict_entries = {}

# Load and process Chinese character data
print("Loading Chinese character data...")
chinese_char_dict = load_chinese_char_dict()

print("Processing Chinese character entries...")
for char_entry in chinese_char_dict.chars:
    char = char_entry.char
    data[char]["c_c"].append(char_entry.to_dict())
    word_index[char]["c"].append(char_entry._id)


print("Loading Kanjidic data...")
kanjidic = load_kanjidic()

print("Processing Kanjidic entries...")
not_found_kanjis = []

for kanji, entry in kanjidic.characters.items():
    if not isinstance(entry, Kanjidic2Character):
        print(
            f"Warning: Unexpected type for entry with key {kanji}. Expected Kanjidic2Character, got {type(entry)}"
        )
        continue

    # Check if the kanji is in the Japanese variants mapping
    japanese_variant = next(
        (item for item in japanese_variants_map if kanji in item), None
    )

    if japanese_variant:
        # Use the traditional Chinese equivalent
        zh_char = japanese_variant[kanji]["t"]
        print(zh_char)
    else:
        # If not in the mapping, use the original kanji
        zh_char = kanji

    # Add the entry under "j_c"
    data[kanji]["j_c"].append(entry.to_dict())

    if zh_char in word_index:
        # Link Japanese and Chinese characters
        data[kanji]["v_c_c"].extend(word_index[zh_char]["c"])
        data[zh_char]["v_j_c"].append(entry.to_dict())
    else:
        # If not found in Chinese dictionary, add to not_found list
        not_found_kanjis.append(kanji)

# ... (keep the JMnedict processing section unchanged)

# Print kanjis not found in the Chinese dictionary
print(f"\nKanjis not found in the Chinese dictionary ({len(not_found_kanjis)}):")
print(", ".join(not_found_kanjis))
