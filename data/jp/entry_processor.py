def clean_and_structure_entry(entry):
    return {
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
                        **({"r": kana.get("romaji", "")} if kana.get("romaji") else {})
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