from collections import Counter, defaultdict, deque
from typing import Any, NamedTuple


class Student(NamedTuple):
    id: int
    name: str
    grade: float


def merge_dicts_sum(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """İki sözlüğü birleştirip ortak anahtarların değerlerini toplar."""
    merged = Counter(d1)
    merged.update(d2)
    return dict(merged)


def group_by_key(
    items: list[dict[str, Any]], key: str
) -> dict[Any, list[dict[str, Any]]]:
    """Liste içindeki sözlükleri verilen anahtara göre gruplar."""
    grouped: defaultdict[Any, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        if key in item:
            grouped[item[key]].append(item)
    return dict(grouped)


def find_top_k_frequent(elements: list[Any], k: int) -> list[Any]:
    """En sık tekrar eden ilk k elemanı döner."""
    return [elem for elem, _ in Counter(elements).most_common(k)]


def invert_dict(d: dict[str, int]) -> dict[int, list[str]]:
    """Sözlükteki key-value ilişkisini tersine çevirir (değerleri anahtar yapar)."""
    inverted: defaultdict[int, list[str]] = defaultdict(list)
    for k, v in d.items():
        inverted[v].append(k)
    return dict(inverted)


def sliding_window_max(nums: list[int], k: int) -> list[int]:
    """O(n) karmaşıklıkta deque kullanarak kayan pencere maksimumlarını bulur."""
    if not nums or k <= 0:
        return []
    result: list[int] = []
    q: deque[int] = deque()

    for i, n in enumerate(nums):
        while q and q[0] <= i - k:
            q.popleft()
        while q and nums[q[-1]] < n:
            q.pop()
        q.append(i)
        if i >= k - 1:
            result.append(nums[q[0]])
    return result


def find_duplicates(elements: list[Any]) -> list[Any]:
    """Listede 1'den fazla geçen elemanları döner."""
    counts = Counter(elements)
    return [k for k, v in counts.items() if v > 1]


def flatten_list(nested_list: list[Any]) -> list[Any]:
    """İç içe geçmiş listeleri düzleştirir."""
    flat: list[Any] = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat


def chunk_list(lst: list[Any], chunk_size: int) -> list[list[Any]]:
    """Listeyi belirtilen boyutlarda alt listelere böler."""
    if chunk_size <= 0:
        return []
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates_ordered(lst: list[Any]) -> list[Any]:
    """Eleman sırasını bozmadan tekrarları siler."""
    return list(dict.fromkeys(lst))


def list_difference(list1: list[Any], list2: list[Any]) -> list[Any]:
    """list1'de olup list2'de olmayan elemanları O(n) sürede döner."""
    s2 = set(list2)
    return [x for x in list1 if x not in s2]


def find_missing_number(nums: list[int], n: int) -> int:
    """1'den n'e kadar olan dizide eksik olan tek sayıyı bulur."""
    expected_sum = n * (n + 1) // 2
    return expected_sum - sum(nums)


def get_deep_value(data: dict[str, Any], path: str, default: Any = None) -> Any:
    """'a.b.c' gibi bir path üzerinden iç içe sözlükten değer çeker."""
    keys = path.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return default
    return curr


def filter_dict_by_keys(d: dict[str, Any], allowed_keys: set[str]) -> dict[str, Any]:
    """Sözlüğü yalnızca izin verilen anahtarlarla filtreler."""
    return {k: v for k, v in d.items() if k in allowed_keys}


def create_student_record(s_id: int, name: str, grade: float) -> Student:
    """NamedTuple formatında öğrenci kaydı üretir."""
    return Student(id=s_id, name=name, grade=grade)


def are_disjoint_lists(l1: list[Any], l2: list[Any]) -> bool:
    """İki listenin hiçbir ortak elemanı olmadığını O(n) sürede doğrular."""
    return set(l1).isdisjoint(set(l2))
