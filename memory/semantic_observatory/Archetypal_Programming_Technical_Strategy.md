# Archetypal Programming — Technical Strategy

## Amaç

Yazılım geliştirmeyi üst-seviye arketiplerden somut uygulamalara uzanan, iki yönlü ve doğrulanabilir bir modelleme süreci olarak ele almak. Görselleştirme bir kullanım alanıdır; **kod üretimi ve biçimsel doğrulama** da sistemin asli hedefleridir.

## Kavramsal hiyerarşi

1. **Archetype:** Kavramsal amaç, roller, ilişkiler, davranışlar ve değişmezler.
2. **Pattern:** Arketipi gerçekleştirebilecek yeniden kullanılabilir yapısal/davranışsal çözüm örüntüleri.
3. **Template:** Belirli dil, framework ve bağlama özgü somutlaştırma şablonları.
4. **Implementation:** Gerçek kaynak kod, testler ve çalışma zamanı davranışı.

Bu ayrım bir **tasarım önerisidir**, yerleşik bir standart değildir. Bir arketip birden fazla örüntüyle, bir örüntü de birden fazla şablonla gerçekleştirilebilir.

## Teknik mimari

```text
Source Code
    ↓
Source Analysis (Python ast / Tree-sitter)
    ↓
Semantic Graph (sınıflar, fonksiyonlar, modüller, ilişkiler)
    ↕
Archetype & Pattern Engine (katalog, kurallar, eşlemeler)
    ↕
World Model (mekânsal / sembolik karşılıklar)
    ↓
Isometric Renderer (Three.js / React Three Fiber)
```

**Not:** `code_graph` henüz mevcut değildir; ileride geliştirilmesi düşünülen bir araçtır. Mevcut bir bileşenmiş gibi varsayılmamalıdır.

## Teknoloji ve görevler

| Katman | Aday teknolojiler | Görev |
|---|---|---|
| Statik analiz | Python `ast`, Tree-sitter | Kod yapılarının çıkarılması |
| Grafik modelleme | NetworkX, JSON | İlişkilerin temsil edilmesi |
| Arketip ve örüntü katalogları | Pydantic, JSON Schema | Yapısal sözleşmeler, sürümleme ve doğrulama |
| Görselleştirme | Three.js, React Three Fiber | 2.5D izometrik dünya |
| Etkileşim | React, Zustand | Keşif ve tasarım arayüzü |
| Çalışma zamanı analizi | Python tracing, pytest | Gerçek çağrıların ve testlerin incelenmesi |
| Kod üretimi/dönüşümü | LLM, LibCST, templates | Tasarımdan kod ve kontrollü değişiklik önerileri |

## Geliştirme aşamaları

### 1. Explore Mode — MVP
Küçük bir Python projesinden modül, sınıf, fonksiyon ve bağımlılıkları çıkar; semantik grafiği üret; izometrik dünyada incelemeyi sağla. İlk sürüm salt okunur olmalı.

### 2. Archetype Engine
`calls → spell activation`, `imports → portal` gibi yapılandırılabilir görsel eşlemeler geliştir. Arketip koleksiyonunda roller, ilişkiler, önkoşullar, sonkoşullar, değişmezler ve ilgili örüntüler bulunabilsin. Semantik model görsel metafordan bağımsız kalsın.

### 3. Construct Mode
Arketip → örüntü → şablon üzerinden kod iskeletleri veya değişiklik önerileri üret. LLM'ler uygun uygulama alternatifleri önerebilir; çıktıların sözleşme, tip, test ve diff kontrollerinden geçmesi gerekir.

### 4. Simulation Mode
Gerçek yürütme izlerini ve test sonuçlarını görsel olaylarla eşleştir. Statik olarak olası görülen davranışlarla çalışma zamanında gözlenen davranışları ayır.

## Arketip koleksiyonu

Her katalog girdisi en az şu alanları taşıyabilir:

- Kimlik, isim, sürüm ve kavramsal açıklama
- Amaç ve kullanım bağlamı
- Roller / varlıklar / ilişkiler
- Önkoşullar, sonkoşullar ve değişmezler
- İlgili örüntüler ve şablonlar
- Örnekler ve karşı-örnekler
- Doğrulama kuralları ve kanıt/test bağlantıları
- İsteğe bağlı görsel metaforlar

Arketipler yalnızca görsel öğe tarifleri değildir; dil-bağımsız tasarım sözleşmeleri olarak da kullanılabilir.

## İki yönlü iş akışı

**Top-down:** Archetype → Pattern → Template → Code → Tests / Validation.

**Bottom-up:** Code → Analysis → Semantic Graph → Pattern Detection → Candidate Archetype.

Bottom-up keşif, otomatik kesin sınıflandırma değil, güven düzeyi ve gerekçesi belirtilen bir öneri olmalıdır.

## Mimari ilkeler

1. **Semantik doğruluk:** Görsel yakınlık veya sembol benzerliği gerçek kod ilişkisi yerine geçmez.
2. **Ayrışma:** Semantic Graph, Archetype Engine ve Renderer bağımsız katmanlar olmalı.
3. **Çoklu dünya:** Aynı model Fantasy World, Architectural Blueprint veya Sci-Fi Network olarak sunulabilmeli.
4. **İzlenebilirlik:** Her üst-seviye öğe ilgili kod, test ve doğrulama sonuçlarına bağlanabilmeli.
5. **Kontrollü üretim:** LLM çıktıları doğrudan doğru kabul edilmemeli; şema, tip, test ve gerektiğinde biçimsel doğrulamadan geçmeli.
6. **İki yönlülük:** Hem tasarımdan uygulamaya hem uygulamadan tasarım modeline ilerlenebilmeli.

## İlk uygulanabilir deney

Bir küçük Python projesi seç; 3–5 arketip tanımla; her arketipe en az bir örüntü ve Python şablonu bağla; örnek kod üret ve test et; ardından kodu yeniden analiz ederek tasarım-kod tutarlılığını ölç. Görsel sahne bu deneyin isteğe bağlı ikinci çıktısı olabilir.

## Açık araştırma sorusu

**Üst-seviye arketipler ile alt-seviye kod arasında, anlamı koruyan, izlenebilir ve doğrulanabilir bir eşleme nasıl kurulabilir?**

Bu soru, projenin görselleştirmeden daha geniş olan esas araştırma hedefidir.
