# Python Gotchas & Pitfalls (40 Tuzak Koleksiyonu)

### 1. Bellek & Değişebilirlik (Mutability)
1. **Mutable Default Argument:** `def append_to(element, target=[]):` ifadesinde varsayılan liste fonksiyon tanım anında tek bir kez oluşturulur. Her çağrıda aynı liste referansı paylaşılır. Çözüm: `target=None` yapıp içeride `if target is None: target = []` kullanmaktır.
2. **List Replication Tuzağı:** `matrix = [[0] * 3] * 3` ifadesi 3 farklı liste üretmez; aynı alt listenin referansını 3 kez kopyalar. `matrix[0][0] = 1` dendiğinde 3 satır birden güncellenir. Doğrusu: `[[0 for _ in range(3)] for _ in range(3)]`.
3. **`is` vs `==` Karşılaştırması:** `==` değer eşitliğini kontrol ederken, `is` nesnelerin bellekteki adreslerinin (`id()`) aynı olup olmadığına bakar.
4. **Small Integer Caching:** CPython `-5` ile `256` arasındaki tamsayıları optimize etmek için önceden belleğe alır (interning). `a = 256; b = 256; a is b -> True` dönerken, `a = 257; b = 257; a is b -> False` dönebilir.
5. **String Interning Farkı:** Standart ASCII tanımlayıcı string'ler CPython tarafından önbelleğe alınırken, boşluk veya özel karakter içeren dizgilerde `is` her zaman `False` verebilir. String eşitliğinde daima `==` kullanılmalıdır.
6. **Shallow vs Deep Copy:** `list.copy()` veya `copy.copy()`, iç içe geçmiş nesnelerin sadece referansını kopyalar. Alt listelerin bağımsız kopyalanması için `copy.deepcopy()` şarttır.
7. **In-place Modification Tuzağı:** `list.sort()` ve `list.reverse()` yerinde değişiklik yapar ve geriye `None` döner. `sorted_list = my_list.sort()` yazıldığında değişken `None` olur.
8. **Tuple İçinde Mutable Nesne:** `t = (1, [2, 3])` tuple'ı immutable olsa bile `t[1].append(4)` çalışır; tuple'ın hash edilebilirliği (hashability) bozulur.
9. **Tuple Birleştirme ve `+=` Hatası:** `t = (1, [2, 3]); t[1] += [4]` çalıştırıldığında hem `TypeError` fırlatılır hem de liste güncellenir (in-place `extend` başarılı olur, atama adımı patlar).
10. **Immutable Dict Key:** Sözlük anahtarları hashable olmak zorundadır. `list` veya `set` anahtar olamaz, ancak `tuple` veya `frozenset` olabilir.

---

### 2. Kapsam (Scoping) & Kapanışlar (Closures)
11. **Late Binding Closures:** Döngü içinde lambda tanımlarken (`funcs = [lambda: i for i in range(3)]`), `i` değişkeni anlık olarak değil, fonksiyon çağrıldığındaki son değeriyle (2) çözümlenir. Çözüm: `lambda i=i: i`.
12. **UnboundLocalError:** Bir fonksiyon içinde bir değişkene atama yapıldığı an Python o değişkeni local kabul eder. Atamadan önce okumaya çalışmak `UnboundLocalError` fırlatır.
13. **`global` vs `nonlocal`:** `global` en dış modül seviyesindeki değişkeni hedeflerken, `nonlocal` iç içe fonksiyonlarda bir üst scope'taki değişkeni değiştirmek için kullanılır.
14. **List Comprehension Değişken Sızıntısı:** Python 2'de comprehension döngü değişkeni dışarı sızıyordu. Python 3'te comprehension kendi izole fonksiyon kapsamına sahiptir; ancak for döngüsü değişkeni dışarı sızmaya devam eder.
15. **Class Scope Fonksiyon İçi Görünmezliği:** Sınıf gövdesinde tanımlanan değişkenler, o sınıfın metotları içindeki comprehension bloklarından doğrudan görülemez.

---

### 3. Akış Kontrolü & Tipler
16. **Float Eşitliği ve Hassasiyet:** `0.1 + 0.2 == 0.3` IEEE 754 kayan nokta standardı nedeniyle `False` döner. Kıyaslama için `math.isclose()` veya finansal hesaplarda `decimal.Decimal` kullanılmalıdır.
17. **Zincirleme Karşılaştırma Mantığı:** `False == False in [False]` ifadesi `(False == False) and (False in [False])` şeklinde genişletilir ve beklenenin aksine `True` döner.
18. **`bool`'un `int` Alt Sınıfı Olması:** `isinstance(True, int)` ifadesi `True` döner. `True + 1 == 2` ve `{1: "a", True: "b"}` sözlüğünde tek anahtar (`1: "b"`) kalır.
19. **`for...else` Bloğu Mantığı:** `for` döngüsünün `else` bloğu döngü başarıyla tamamlandığında çalışır; eğer döngüden `break` ile çıkıldıysa `else` bloğu çalıştırılmaz.
20. **`try...finally` Dönüş Değeri Ezmesi:** `try` bloğu `return 1` dese bile, `finally` bloğu içine `return 2` yazılırsa fonksiyon `2` döner; `try`'ın dönüş değeri tamamen ezilir.

---

### 4. Koleksiyonlar & İterasyon
21. **İterasyon Sırasında Sözlük Boyutunu Değiştirmek:** `for k in d: del d[k]` doğrudan `RuntimeError: dictionary changed size during iteration` fırlatır. Silme için `list(d.keys())` üzerinden dönülmelidir.
22. **Generator'ın Tek Seferlik Tüketimi:** Generator'lar bellekte veri tutmaz, bir kez iterate edildiklerinde tükenirler. İkinci kez `for` döngüsüne sokulduklarında boş dönerler.
23. **`zip`'in En Kısa Dizide Kesilmesi:** Standart `zip(a, b)` dizilerden biri bittiğinde sessizce durur. Veri kaybını önlemek için eksik elemanları dolduran `itertools.zip_longest` kullanılmalıdır.
24. **`itertools.groupby` Ön Sıralama Şartı:** `itertools.groupby` SQL'deki `GROUP BY` gibi çalışmaz; yalnızca ardışık aynı elemanları gruplar. Kullanmadan önce listenin o anahtara göre sıralanması (`sorted()`) şarttır.
25. **`dict` Sıralama Garantisi:** Python 3.7+ ile sözlükler ekleme sırasını korur; ancak iki sözlüğün eşitliğinde (`d1 == d2`) sıra önemsizdir.

---

### 5. OOP & Dunder Metotlar
26. **Class Variable vs Instance Variable Paylaşımı:** Sınıf seviyesinde `data = []` tanımlanır ve `self.data.append()` yapılırsa tüm örnekler aynı listeyi paylaşır. Instance değişkenleri `__init__` içinde `self.data = []` ile ayrılmalıdır.
27. **`__eq__` Override Edildiğinde `__hash__`'in Kaybolması:** Bir sınıfta `__eq__` tanımlanıp `__hash__` tanımlanmazsa, o sınıfın örnekleri hashable olmaktan çıkar ve sözlük anahtarı veya set elemanı olamaz.
28. **`super()` Çoklu Kalıtım ve MRO (Method Resolution Order):** `super()` doğrudan üst sınıfı değil, C3 Lineerleştirme algoritmasıyla belirlenen MRO sırasındaki bir sonraki sınıfı çağırır.
29. **`__slots__` ve Dinamik Nitelikler:** `__slots__` tanımlandığında `__dict__` oluşmaz; bellek ciddi oranda düşer ancak sınıfa dinamik olarak yeni nitelik (`self.new_attr = 5`) eklenemez.
30. **`__del__` Destructor Güvensizliği:** `__del__` metodunun nesne bellekten silindiği an çalışacağı garanti değildir (dairesel referanslar garbage collector'ı geciktirebilir). Kaynak temizliği için context manager (`with`) tercih edilmelidir.

---

### 6. Exception & Hata Yönetimi
31. **Çıplak `except:` Tuzağı:** `except:` veya `except Exception:` yerine doğrudan bare except yazmak `KeyboardInterrupt` (Ctrl+C) ve `SystemExit` sinyallerini de yakalar; programı terminalden durdurmayı imkansız kılar.
32. **Exception Zincirleme (`raise ... from None`):** Bir hatayı yakalayıp yeni bir hata fırlatırken bağlamı temiz tutmak için `raise CustomError from None`, orijinal hatanın izini korumak için `raise CustomError from err` kullanılmalıdır.
33. **Context Manager Exception Bastırma:** `__exit__` metodu `True` dönerse, `with` bloğu içinde oluşan hata sessizce yutulur; `False` veya `None` dönerse hata yukarı fırlatılır.

---

### 7. Tip Sistemi & Asenkron Mimari
34. **`None` Karşılaştırmalarında Tip Daraltma:** `if x:` kontrolü `0`, `""`, `[]` gibi falsy değerleri de yakalar. Sadece `None` kontrolü için `if x is not None:` yazılmalıdır.
35. **Type Hint Runtime'da Doğrulama Yapmaz:** Standart Python'da `x: int = "yazı"` kodu hata vermeden çalışır. Runtime doğrulama için Pydantic gibi araçlar gerekir.
36. **`asyncio.gather` Hata Davranışı:** `gather` varsayılan olarak bir task patladığında diğer çalışan task'ları iptal etmez. Hataları toplamak için `return_exceptions=True` parametresi verilmelidir.
37. **Async Kodda Bloklayıcı Çağrılar:** `async def` içinde `time.sleep()` veya `requests.get()` gibi senkron bloklayıcı kütüphaneler kullanmak tüm event loop'u dondurur. `asyncio.sleep()` ve `httpx` kullanılmalıdır.
38. **Fire-and-forget Async Task Garbage Collection:** `asyncio.create_task(coro())` çağrıldığında task referansı bir değişkende tutulmazsa, çalışma esnasında Python Garbage Collector tarafından toplanıp sessizce yok edilebilir.

---

### 8. Import & Modül Yapısı
39. **Dairesel Import (Circular Import):** İki modül birbirini dosya başında import ederse `ImportError` oluşur. Çözüm: Modül içi fonksiyon seviyesinde lazy import yapmak veya bağımlılığı üçüncü bir core/types modülüne ayırmaktır.
40. **Gölgeleme (Module Shadowing):** Kendi script dosyana `math.py`, `random.py` veya `json.py` adı verirsen, standart kütüphaneyi gölgeler ve tüm üçüncü parti kütüphanelerin import adımlarını kırarsın.