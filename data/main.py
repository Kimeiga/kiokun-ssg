import json
from collections import defaultdict
from pathlib import Path
import argparse

from data.jp.jmdict import load_jmdict, JMdictEntry
from data.jp.kanjidic import load_kanjidic, Kanjidic2Character
from data.jp.jmnedict import load_jmnedict, JMnedictWord
from data.zh.char_dict import load_chinese_char_dict
from data.zh.word_dict import load_chinese_word_dict

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

print("hiiii")

# Load j2ch mapping and exceptions
with open("data/j2ch/j2ch.json", "r", encoding="utf-8") as file:
    j2ch = json.load(file)

# with open("data/j2ch/j2ch_new_min.json", "r", encoding="utf-8") as file:
#     j2ch_new = json.load(file)

# with open("data/jp/j_exceptions.json", "r", encoding="utf-8") as file:
#     j_exceptions = json.load(file)

print("hello")

j_exceptions = {
    "仮託": "假託",  # 仮託
    "帰依": "歸依",  # 帰依, chosen because 歸依 is HSK 4, and 皈依 is not in HSK
    "結髪": "結髮",  # 結髪, 髮 and 髮 differ by one tiny stroke on top right of the 犮
    "元勲": "元勛",  # 元勲, src: wiktionary
    "広州": "廣州",  # 広州
    "行政区画": "行政區劃",  # 行政区画
    "賛同": "贊同",  # 賛同
    "製図": "製圖",  # 製図
    "素麺": "素麵",  # 素麺
    "痴呆": "痴呆",  # 痴呆 https://zh.wikipedia.org/wiki/%E5%A4%B1%E6%99%BA%E7%97%87
    "弁証": "辯證",  # 弁証
    "砲撃": "炮擊",  # 砲撃
    # 招来 apparently 招來 is an alternate form (src wiktionary) and baike's 招徠 entry is way longer
    "招来": "招徠",
    "発布": "發布",  # 発布
    "分布図": "分佈圖",
    "冷麺": "冷麵",  #
    "身分証": "身份證",  #
    "台子": "檯子",  #
    # jmnedict
    "円月": "元月",
    "径直": "徑直",
    "広安": "廣安",
    "広元": "廣元",
    "広陽": "廣陽",
    "日円": "日元",
    "弁別": "辨別",
    "輪廻": "輪迴",
    "剣尖": "劍尖",
    "不穏": "不穩",
    "応変": "應變",
    "散発": "散發",
    "平穏": "平穩",
    "収獲": "收獲",
    "収穫": "收穫",
    "旧制": "舊制",
    "暗々": "暗暗",
    "声誉": "聲譽",
    "自尽": "自盡",
    "燻蒸剤": "燻蒸劑",
    "余熱": "餘熱",
    "余震": "餘震",
    "発毛": "發毛",
}


def j2ch_get(j):
    return j2ch.get(j, j)


print("hi again")


def generate_combinations2(key):
    return ["".join(j2ch_get(char) for char in key)]


def filter_entries(combinations, index):
    return [comb for comb in combinations if comb in index]


def get_j2ch_word(key, index):
    if key in j_exceptions:
        return [j_exceptions[key]]
    combinations = generate_combinations2(key)
    return filter_entries(combinations, index)


print("welcome")

# # Get the directory of the script
# script_dir = Path(__file__).resolve().parent
# output_dir = script_dir.parent / "dictionary"

# print(f"Output directory: {output_dir}")

data = defaultdict(lambda: defaultdict(list))
word_index = defaultdict(lambda: defaultdict(list))
jmdict_entries = {}

# Load and process Chinese character data
print("Loading Chinese character data...")
chinese_char_dict = load_chinese_char_dict()

print("Processing Chinese character entries...")
for char_entry in chinese_char_dict.chars:
    char = char_entry.char
    char_dict = char_entry.to_dict()

    if char_entry.simp_variants:
        # This is a traditional character
        data[char]["c_tc"].append(char_dict)
        word_index[char]["c"].append(char_entry._id)

        for simp in char_entry.simp_variants:
            data[simp]["c_sc"].append(char_dict)
            word_index[simp]["c"].append(char_entry._id)
    elif char_entry.trad_variants:
        # This is a simplified character
        data[char]["c_sc"].append(char_dict)
        word_index[char]["c"].append(char_entry._id)

        for trad in char_entry.trad_variants:
            data[trad]["c_tc"].append(char_dict)
            word_index[trad]["c"].append(char_entry._id)
    else:
        # This character is neither explicitly traditional nor simplified
        data[char]["c_tc"].append(char_dict)
        word_index[char]["c"].append(char_entry._id)

# Load and process Chinese word data
print("Loading Chinese word data...")
chinese_word_dict = load_chinese_word_dict()

print("Processing Chinese word entries...")
for word_entry in chinese_word_dict.words:
    trad = word_entry.trad
    simp = word_entry.simp

    data[trad]["c_w"].append(word_entry.to_dict())
    word_index[trad]["c"].append(word_entry._id)

    # Add simplified form if different from traditional
    if simp != trad:
        data[simp]["c_w"].append(word_entry.to_dict())
        word_index[simp]["c"].append(word_entry._id)

print("Loading JMdict data...")
jmdict = load_jmdict()

print("Processing JMdict entries...")

for index, entry in enumerate(jmdict.words):
    if not isinstance(entry, JMdictEntry):
        print(
            f"Warning: Unexpected type for entry at index {index}. Expected JMdictEntry, got {type(entry)}"
        )
        continue

    keys = []

    # Add all kanji representations
    if entry.kanji:
        for kanji in entry.kanji:
            keys.append(kanji.text)
            word_index[kanji.text]["j"].append(index)

    # Add all kana representations
    if entry.kana:
        for kana in entry.kana:
            keys.append(kana.text)
            word_index[kana.text]["j"].append(index)

    # If no keys were found, skip this entry
    if not keys:
        print(f"Warning: No keys found for entry at index {index}")
        continue

    # Add the entry to each key under "j_w"
    for key in keys:
        data[key]["j_w"].append(entry.to_dict())

        # Try to find Chinese equivalents
        zh_keys = get_j2ch_word(key, word_index)
        for zh_key in zh_keys:
            if zh_key in word_index:
                # Link Japanese and Chinese entries
                data[key]["v_c_w"].extend(word_index[zh_key]["c"])
                data[zh_key]["v_j_w"].append(index)

print("Loading Kanjidic data...")
kanjidic = load_kanjidic()

# Modify the Kanjidic processing part
print("Processing Kanjidic entries...")

for kanji, entry in kanjidic.characters.items():
    if not isinstance(entry, Kanjidic2Character):
        print(
            f"Warning: Unexpected type for entry with key {kanji}. Expected Kanjidic2Character, got {type(entry)}"
        )
        continue

    # Add the entry under "j_c"
    data[kanji]["j_c"].append(entry.to_dict())

    # Try to find Chinese equivalent
    zh_char = j2ch_get(kanji)
    if zh_char in word_index:
        # Link Japanese and Chinese characters
        if "c_tc" in data[zh_char]:
            data[kanji]["v_c_tc"].extend(word_index[zh_char]["c"])
        if "c_sc" in data[zh_char]:
            data[kanji]["v_c_sc"].extend(word_index[zh_char]["c"])
        data[zh_char]["v_j_c"].append(entry.to_dict())

print("Loading JMnedict data...")
jmnedict = load_jmnedict()

print("Processing JMnedict entries...")

for index, entry in enumerate(jmnedict.words):
    if not isinstance(entry, JMnedictWord):
        print(
            f"Warning: Unexpected type for entry at index {index}. Expected JMnedictWord, got {type(entry)}"
        )
        continue

    keys = []

    # Add all kanji representations
    for kanji in entry.kanji:
        keys.append(kanji.text)

    # Add all kana representations
    for kana in entry.kana:
        keys.append(kana.text)

    # If no keys were found, skip this entry
    if not keys:
        print(f"Warning: No keys found for JMnedict entry at index {index}")
        continue

    # Add the entry to each key under "j_n"
    for key in keys:
        data[key]["j_n"].append(entry.to_dict())

        # Try to find Chinese equivalents
        zh_keys = get_j2ch_word(key, word_index)
        for zh_key in zh_keys:
            if zh_key in word_index:
                # Link Japanese and Chinese entries
                data[key]["v_c_n"].extend(word_index[zh_key]["c"])
                data[zh_key]["v_j_n"].append(index)


output_dir.mkdir(parents=True, exist_ok=True)

print("Writing JSON files...")
total_processed = 0
for key, entries in data.items():
    with open(output_dir / f"{key}.json", "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))

    total_processed += 1

print(f"Total processed entries: {total_processed}")
print(f"Dictionary files have been written to: {output_dir}")
