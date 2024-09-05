import json
import os
import gzip
import sys
from collections import defaultdict
from pathlib import Path

import jaconv

from .jp.kanjidic.types import load_kanjidic
from .jp.jmdict.types import load_jmdict
from .utils import is_hanzi

# Get the project root directory
project_root = Path(__file__).parents[1]

data = defaultdict(list)
word_index = defaultdict(lambda: defaultdict(list))
jmdict_entries = {}

jmdict = load_jmdict()
kanjidic = load_kanjidic()

for entry in jmdict.words:
    # Check if the entry has kanji representations
    if entry.kanji:
        # check if the entry is only a single kanji character
        if all(len(kanji.text) == 1 for kanji in entry.kanji):
            kanji = entry.kanji[0].text
            if is_hanzi(kanji):
                # this kanji is a Chinese character

                # get the kanjidic entry for this kanji
                char_entry = kanjidic.get_character(kanji)

                if not char_entry:
                    print(f"Kanji {kanji} not found in kanjidic")
                    continue

                # print(entry.kana)

                if any(
                    jaconv.hira2kata(kana) in char_entry.reading_meaning.onyomi
                    for kana in entry.get_all_kana()
                ):
                    print(entry.to_dict())
