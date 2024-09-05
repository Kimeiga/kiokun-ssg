from .types import load_kanjidic


def test_load_kanjidic():
    kanjidic = load_kanjidic()

    # check to see if there is ever an entry where there is len(entry.readingMeaning.groups) > 1
    for _, entry in kanjidic.characters.items():
        if len(entry.reading_meaning.groups) != 1:
            print(entry)
            break


test_load_kanjidic()
