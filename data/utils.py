class HanziKanjiChars:
    """
    An object that enumerates the code points of Hanzi/Kanji characters.
    """
    # CJK Unified Ideographs (4E00–9FFF)
    CJK_Unified_Ideographs = (0x4E00, 0x9FFF)
    
    # CJK Unified Ideographs Extension A (3400–4DBF)
    CJK_Unified_Ideographs_Extension_A = (0x3400, 0x4DBF)
    
    # CJK Unified Ideographs Extension B (20000–2A6DF)
    CJK_Unified_Ideographs_Extension_B = (0x20000, 0x2A6DF)
    
    # CJK Unified Ideographs Extension C (2A700–2B73F)
    CJK_Unified_Ideographs_Extension_C = (0x2A700, 0x2B73F)
    
    # CJK Unified Ideographs Extension D (2B740–2B81F)
    CJK_Unified_Ideographs_Extension_D = (0x2B740, 0x2B81F)
    
    # CJK Unified Ideographs Extension E (2B820–2CEAF)
    CJK_Unified_Ideographs_Extension_E = (0x2B820, 0x2CEAF)
    
    # CJK Unified Ideographs Extension F (2CEB0–2EBEF)
    CJK_Unified_Ideographs_Extension_F = (0x2CEB0, 0x2EBEF)
    
    # CJK Compatibility Ideographs (F900–FAFF)
    CJK_Compatibility_Ideographs = (0xF900, 0xFAFF)

    ranges = [
        CJK_Unified_Ideographs,
        CJK_Unified_Ideographs_Extension_A,
        CJK_Unified_Ideographs_Extension_B,
        CJK_Unified_Ideographs_Extension_C,
        CJK_Unified_Ideographs_Extension_D,
        CJK_Unified_Ideographs_Extension_E,
        CJK_Unified_Ideographs_Extension_F,
        CJK_Compatibility_Ideographs
    ]

def is_hanzi(character):
    """
    Checks whether a character is a Hanzi/Kanji.

    >>> is_hanzi('漢')
    True
    >>> is_hanzi('ア')
    False
    >>> is_hanzi('A')
    False

    :param character: The character that needs to be checked.
    :type character: str
    :return: bool
    """
    return any(start <= ord(character) <= end for start, end in HanziKanjiChars.ranges)


"""
>>> from utils import is_hanzi
>>> is_hanzi('あ')
False
>>> is_hanzi('ア')
False
>>> is_hanzi('亜')
True
>>> is_hanzi('ㄨ')
False
>>> is_hanzi('a')
False
"""

