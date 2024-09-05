# import romkan

# def process_japanese_entry(entry, index, word_index):
#     keys = []

#     # Add all kanji representations
#     for kanji in entry.get("kanji", []):
#         keys.append(kanji["text"])
#         word_index[kanji["text"]]["j"].append(index)

#     # Add all kana representations
#     for kana in entry.get("kana", []):
#         keys.append(kana["text"])
#         word_index[kana["text"]]["j"].append(index)
#         kana["romaji"] = romkan.to_roma(kana["text"])

#     # If no keys were found, skip this entry
#     if not keys:
#         return None

#     return {"keys": keys, "entry": entry}


from pathlib import Path
from pprint import pprint
from jmdict import JMdict, load_jmdict

# Get the project root directory
project_root = Path(__file__).parents[2]

# Define paths
databases_dir = project_root / 'databases'
jmdict_file = databases_dir / 'jmdict-eng-3.5.0.json'

# Load JMdict
jmdict = load_jmdict(str(jmdict_file))

# Your main code here
for entry in jmdict.words[:5]:  # Let's just print the first 5 entries as an example
    print(f"ID: {entry.id}")
    print(entry)
    print(entry.to_dict())
    print("---")