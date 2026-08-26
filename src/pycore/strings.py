import re
from collections import Counter


def is_palindrome(text: str) -> bool:
    """Alfanümerik karakterleri dikkate alarak palindrom kontrolü yapar."""
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text).lower()
    return cleaned == cleaned[::-1]


def reverse_words(sentence: str) -> str:
    """Cümledeki kelimelerin sırasını tersine çevirir, fazla boşlukları temizler."""
    return " ".join(sentence.strip().split()[::-1])


def count_vowels_and_consonants(text: str) -> dict[str, int]:
    """Sesli ve sessiz harf sayılarını döner."""
    vowels = set("aeiouAEIOU")
    v_count = sum(1 for char in text if char in vowels)
    c_count = sum(1 for char in text if char.isalpha() and char not in vowels)
    return {"vowels": v_count, "consonants": c_count}


def are_anagrams(str1: str, str2: str) -> bool:
    """İki stringin anagram olup olmadığını kontrol eder."""
    clean1 = re.sub(r"[^a-zA-Z0-9]", "", str1).lower()
    clean2 = re.sub(r"[^a-zA-Z0-9]", "", str2).lower()
    return Counter(clean1) == Counter(clean2)


def run_length_encode(text: str) -> str:
    """Basit Run-Length Encoding sıkıştırması yapar."""
    if not text:
        return ""
    result: list[str] = []
    current_char = text[0]
    current_count = 1
    for char in text[1:]:
        if char == current_char:
            current_count += 1
        else:
            result.append(f"{current_char}{current_count}")
            current_char = char
            current_count = 1
    result.append(f"{current_char}{current_count}")
    return "".join(result)


def run_length_decode(encoded: str) -> str:
    """Run-Length Encoding ile sıkıştırılmış metni açar."""
    if not encoded:
        return ""
    pairs = re.findall(r"([a-zA-Z])(\d+)", encoded)
    return "".join(char * int(count) for char, count in pairs)


def truncate_string(text: str, max_len: int) -> str:
    """Metni belirtilen uzunlukta kesip sonuna '...' ekler."""
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    return text[: max_len - 3] + "..."


def to_snake_case(camel_str: str) -> str:
    """camelCase veya PascalCase stringi snake_case formatına çevirir."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def find_first_non_repeating(text: str) -> str | None:
    """Tekrarlanmayan ilk karakteri döner."""
    counts = Counter(text)
    for char in text:
        if counts[char] == 1:
            return char
    return None


def mask_sensitive_data(
    card_number: str, visible_start: int = 0, visible_end: int = 4
) -> str:
    """Hassas bilgileri maskeler."""
    digits = re.sub(r"\s+", "", card_number)
    if len(digits) <= (visible_start + visible_end):
        return digits
    masked_part = "*" * (len(digits) - visible_start - visible_end)
    return (
        digits[:visible_start]
        + masked_part
        + (digits[-visible_end:] if visible_end > 0 else "")
    )


def tokenize_words(text: str) -> list[str]:
    """Metni noktalama işaretlerinden arındırıp küçük harfli kelime listesine böler."""
    return re.findall(r"\b\w+\b", text.lower())
