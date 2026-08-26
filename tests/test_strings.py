from pycore.strings import (
    are_anagrams,
    count_vowels_and_consonants,
    find_first_non_repeating,
    is_palindrome,
    mask_sensitive_data,
    reverse_words,
    run_length_decode,
    run_length_encode,
    to_snake_case,
    tokenize_words,
    truncate_string,
)


def test_is_palindrome() -> None:
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome("") is True


def test_reverse_words() -> None:
    assert reverse_words("the sky is blue") == "blue is sky the"
    assert reverse_words("  hello world  ") == "world hello"


def test_count_vowels_and_consonants() -> None:
    assert count_vowels_and_consonants("hello") == {"vowels": 2, "consonants": 3}
    assert count_vowels_and_consonants("123! ") == {"vowels": 0, "consonants": 0}


def test_are_anagrams() -> None:
    assert are_anagrams("listen", "silent") is True
    assert are_anagrams("triangle", "integral") is True
    assert are_anagrams("apple", "pale") is False


def test_rle_encode_decode() -> None:
    raw = "AAABBBCCDAA"
    encoded = run_length_encode(raw)
    assert encoded == "A3B3C2D1A2"
    assert run_length_decode(encoded) == raw


def test_truncate_string() -> None:
    assert truncate_string("Hello World", 8) == "Hello..."
    assert truncate_string("Hi", 5) == "Hi"
    assert truncate_string("DataScience", 3) == "Dat"


def test_to_snake_case() -> None:
    assert to_snake_case("camelCase") == "camel_case"
    assert to_snake_case("PascalCaseExample") == "pascal_case_example"
    assert to_snake_case("already_snake") == "already_snake"


def test_find_first_non_repeating() -> None:
    assert find_first_non_repeating("swiss") == "w"
    assert find_first_non_repeating("aabbcc") is None


def test_mask_sensitive_data() -> None:
    assert mask_sensitive_data("1234567812345678") == "************5678"
    assert mask_sensitive_data("12345678", visible_start=2, visible_end=2) == "12****78"


def test_tokenize_words() -> None:
    assert tokenize_words("Hello, World! Welcome to Python.") == [
        "hello",
        "world",
        "welcome",
        "to",
        "python",
    ]
