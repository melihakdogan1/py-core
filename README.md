# py-core & mini-etl

Python ileri seviye yazılım mühendisliği disiplini, veri yapıları, eşzamanlılık (async/multiprocessing), statik tip denetimi (`mypy --strict`) ve generator tabanlı streaming ETL kütüphanesi (`mini-etl`).

---

## 1. Mimari ve Bileşenler

### A. Çekirdek Modüller (`src/pycore/`)
* **`strings.py`**: String manipülasyonları, RLE kodlama/kod çözme, hassas veri maskeleme algoritmaları.
* **`collections.py`**: Frekans analizleri, kayan pencere algoritmaları, derin sözlük erişimi, `deque` optimizasyonları.
* **`generators.py`**: Lazy evaluation, chunked stream operasyonları, Fibonacci ve kartezyen çarpım generator'ları.
* **`decorators.py`**: Argümanlı/argümansız dekoratörler, `functools.wraps` korumalı sayaç/süre ölçerler, LRU bellek ve context manager'lar.
* **`oop.py`**: Dunder metotlar (`__repr__`, `__len__`, `__iter__`, `__matmul__`), immutable dataclass'lar ve ABC arayüzleri.
* **`types.py`**: Generic result container'ları, Duck typing ve `Protocol` yapısal alt tipleme desenleri.
* **`asyncs.py`**: Event loop yapıları, `asyncio.gather`, timeout korumalı eşzamanlı veri çekme mekanizmaları.

### B. Mini ETL Framework (`src/minietl/`)
Yalnızca standart kütüphane ve `Protocol` mimarisi kullanılarak geliştirilmiş generator tabanlı akış kütüphanesi:
* **Source (`Protocol`)**: `CsvSource`, `JsonlSource` ve `HttpSource` veri kaynakları.
* **Transform Zinciri (`>>`)**: `map`, `filter`, `validate`, `rename` ve `cast` adımlarının `__rshift__` operatörüyle kompozisyonu.
* **Sink (`Protocol`)**: `CsvSink`, `SqliteSink` ve `StdoutSink` veri hedefleri.
* **Hata & Dead-Letter Mekanizması**: Satır bazlı hata toplama, şema bozulmalarında satır reddi ve exponential backoff retry.
* **CLI Entegrasyonu**: `typer` ile yapılandırılmış `mini-etl run --config pipeline.yaml` komut satırı arayüzü.

---

## 2. Bellek Tüketimi ve Benchmark Analizleri

### 1 GB Log Dosyası Agregasyon Karşılaştırması (Ödev 2.3)

| Yöntem | Süre (sn) | Tepe Bellek (Peak RAM) | Açıklama |
| :--- | :--- | :--- | :--- |
| **Naif Satır Döngüsü** | 89.50 sn | ~12.4 MB | Standart dosya okuma ve dict boyutu |
| **Generator + Counter** | 73.10 sn | **~3.2 MB** | C-seviyesinde sayaç ve lazy stream |
| **Multiprocessing (Chunking)** | 73.50 sn | ~14.8 MB | CPU çekirdekleri arası byte ofset bölmesi |
| **Polars (Streaming Engine)** | **1.52 sn** | ~68.0 MB | Rust vektörize bellek haritalama ve lazy query |

Bellek Tüketimi (Düşük olan daha iyi):
* Generator + Counter : [■■] 3.2 MB
* Naif Satır Döngüsü  : [■■■■■■] 12.4 MB
* Multiprocessing     : [■■■■■■■] 14.8 MB
* Polars (Streaming)  : [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 68.0 MB

Süre (Hızlı olan daha iyi):
* Polars (Streaming)  : [■] 1.52 sn
* Generator + Counter : [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 73.1 sn

### Senkron vs Asenkron API İstemcisi Benchmarkı (Ödev 2.4)

| Yöntem | Toplam Süre (sn) | Başarılı İstek | Throughput (İstek/sn) |
| :--- | :--- | :--- | :--- |
| **Senkron (`requests.Session`)** | 39.79 sn | 200 / 200 | 5.0 req/s |
| **Asenkron (`httpx` + `Semaphore(10)`)** | **2.78 sn** | 200 / 200 | **72.0 req/s (~14.3x)** |

---

## 3. Test ve Kalite Standartları

* **Test Coverage:** `%90+` (Pytest + Hypothesis property-based testing)
* **Static Typing:** `mypy --strict` (0 hata, 14 kaynak dosya)
* **Linting & Formatting:** `ruff` (E, F, I kuralları)

```bash
# Testleri ve coverage raporunu çalıştırma
uv run pytest -v --cov=src

# Statik tip denetimi
uv run mypy src

# Lint ve format kontrolleri
uv run ruff check . && uv run ruff format --check .