from enum import Enum


class SqlCmpOptions(Enum):
    """
    Specifies the SQL compare options.
    """
    NONE = 1
    """
    Specifies the default option settings for SqlString comparisons.
    """
    IGNORE_CASE = 2
    """
    Specifies that SqlString comparisons must ignore case.
    """
    IGNORE_NON_SPACE = 3
    """
    Specifies that SqlString comparisons must ignore non-space combining characters, such as diacritics. The Unicode
    Standard defines combining characters as characters that are combined with base characters to produce a new
    character. Non-space combining characters do not use character space by themselves when rendered. For more
    information about non-space combining characters, see the Unicode Standard at https://www.unicode.org.
    """
    IGNORE_KANA_TYPE = 9
    """
    Specifies that System.Data.SqlTypes.SqlString comparisons must ignore the Kana type. Kana type refers to Japanese
    hiragana and katakana characters that represent phonetic sounds in the Japanese language. Hiragana is used for
    native Japanese expressions and words, while katakana is used for words borrowed from other languages, such as
    "computer" or "Internet". A phonetic sound can be expressed in both hiragana and katakana. If this value is
    selected, the hiragana character for one sound is considered equal to the katakana character for the same sound.
    """
    IGNORE_WIDTH = 17
    """
    Specifies that System.Data.SqlTypes.SqlString comparisons must ignore the character width. For example, Japanese
    katakana characters can be written as full-width or half-width and, if this value is selected, the katakana
    characters written as full-width are considered equal to the same characters written in half-width.
    """
    BINARY_SORT_2 = 16385
    """
    Performs a binary sort
    """
    BINARY_SORT = 32769
    """
    Specifies that sorts should be based on a characters numeric value instead of its alphabetical value
    """
