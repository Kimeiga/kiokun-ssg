import json
import re
from pathlib import Path
from data.zh.char_dict import load_chinese_char_dict, ChineseCharEntry


def is_japanese_variant(char_entry: ChineseCharEntry) -> bool:
    if char_entry.statistics and char_entry.statistics.top_words:
        first_top_word = char_entry.statistics.top_words[0]
        return first_top_word.gloss.startswith("Japanese variant of")
    return False


def extract_chinese_equivalents(gloss: str) -> tuple:
    # Regular expression to match the Chinese characters
    match = re.search(r"of\s+([^\[]+)(?:\[|$)", gloss)
    if match:
        chars = match.group(1).split("|")
        if len(chars) == 2:
            return chars[0], chars[1]  # Traditional, Simplified
        elif len(chars) == 1:
            return chars[0], chars[0]  # Same character for both
    return None, None


def find_japanese_variants():
    chinese_char_dict = load_chinese_char_dict()
    japanese_variants = []
    skipped_entries = []

    print("Scanning Chinese character dictionary for Japanese variants...")
    for char_entry in chinese_char_dict.chars:
        if is_japanese_variant(char_entry):
            gloss = char_entry.statistics.top_words[0].gloss
            trad, simp = extract_chinese_equivalents(gloss)
            if trad and simp:
                japanese_variants.append({char_entry.char: {"t": trad, "s": simp}})
            else:
                skipped_entries.append((char_entry.char, gloss))

    print(f"Found {len(japanese_variants)} Japanese variants.")
    print(f"Skipped {len(skipped_entries)} entries.")
    return japanese_variants, skipped_entries


def save_japanese_variants(japanese_variants, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(japanese_variants, f, ensure_ascii=False, indent=2)
    print(f"Japanese variants mapping saved to {output_file}")


def save_skipped_entries(skipped_entries, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(skipped_entries, f, ensure_ascii=False, indent=2)
    print(f"Skipped entries saved to {output_file}")


if __name__ == "__main__":
    japanese_variants, skipped_entries = find_japanese_variants()

    # Save the results
    script_dir = Path(__file__).resolve().parent
    output_file = script_dir / "japanese_variants_mapping.json"
    save_japanese_variants(japanese_variants, output_file)

    skipped_file = script_dir / "skipped_japanese_variants.json"
    save_skipped_entries(skipped_entries, skipped_file)

    # Print some examples
    print("\nExample Japanese variants mapping:")
    for i, var in enumerate(japanese_variants[:5], 1):
        for jp, ch in var.items():
            print(f"{i}. {jp}: Traditional - {ch['t']}, Simplified - {ch['s']}")

    print("\nExample skipped entries:")
    for i, (char, gloss) in enumerate(skipped_entries[:5], 1):
        print(f"{i}. {char}: {gloss}")

    # Print statistics
    total_chars = len(load_chinese_char_dict().chars)
    percent_japanese = (len(japanese_variants) / total_chars) * 100
    print(f"\nTotal characters in dictionary: {total_chars}")
    print(f"Number of Japanese variants: {len(japanese_variants)}")
    print(f"Number of skipped entries: {len(skipped_entries)}")
    print(f"Percentage of Japanese variants: {percent_japanese:.2f}%")
