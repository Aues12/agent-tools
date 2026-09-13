# Ontology Pyramid

## Temel Fikir

Ontoloji, yalnızca kavramların birbirleriyle ilişkilerini gösteren formsuz bir graph olarak değil, **dikey yönelime sahip bir Piramit** olarak düşünülebilir.

Bu modelde iki farklı semantik hareket birbirinden ayrılır:

- **Yatay hareket:** Aynı ontolojik düzeydeki kavramların birbirleriyle ilişkileri.
- **Dikey hareket:** Bir kavramın, kendisini mümkün kılan veya anlamlandıran daha yüksek Anlam/Form/İlke'ye yönelmesi.

Dolayısıyla graph ortadan kaldırılmaz. **Graph'a ontolojik bir geometri ve yönelim kazandırılır.**

---

## Veri ve Bilgi Ayrımı

Veri ve Bilgi aynı şey değildir.

> **Bilgi, esasen Veri'nin Zihin'de yapılandırılması sonucunda tezahür eder.**

Veri yatay düzleme aittir. Bilgi ise Yaratıcı'nın Logos'una (Kelâm'ına) yakınlığı ölçüsünde farklı **Ontolojik Seviyeler** kazanır.

Bu nedenle:

**Veri → Yapılandırma → Bilgi → Ontolojik Yükseliş**

şeklinde bir epistemik hareket düşünülebilir.

Bilgi miktarının artması yalnızca daha fazla veri biriktirmek anlamına gelmez. Verinin daha yüksek anlam düzeyleri altında bütünleştirilmesi gerekir.

---

## Piramit Geometrisi

Piramit'in Tepe Noktası boyutsuz bir **Referans Noktası**dır.

Alt katmanlar genişleyebilir, yeni bilgiler ve yeni domainler eklenebilir; fakat Referans Noktası değişmez. Böylelikle Piramit'in hacmi büyürken **Asıl Şekil'in oranları, bütünlüğü ve dengesi korunabilir.**

```text
                         ●
                  Referans Noktası
                         │
                       İlke
                      /   \
                   Form   Form
                  /  │     │  \
              Kavram Kavram Kavram
              / │ \    │    / │ \
             /  │  \   │   /  │  \
        ───────────────────────────────
                  Veri / Gözlem
```

Piramit büyüdükçe gözlemcinin **Ufku** genişler.

Dolayısıyla ontology'nin genişlemesi kendi başına bir problem değildir. Temel invariant şudur:

> **Bilgi alanı genişleyebilir; ontolojik yönelim bozulmamalıdır.**

---

## Graph ve Piramit

Semantica benzeri ontology sistemleri, belirli bir domain hakkındaki **Zihin/Fikir Modeli** olarak düşünülebilir.

Örneğin:

```text
Person
├── worksFor → Organization
├── livesAt → Location
├── knows → Person
└── hasRole → Occupation
```

Bu graph, kavramların birbirleriyle ilişkilerini başarıyla temsil eder.

Fakat kendi başına şu sorulara cevap vermek zorunda değildir:

- Hangisi ontolojik olarak daha temeldir?
- Hangisi diğerinin açıklayıcı ilkesidir?
- Hangi yöne gidildiğinde bilgi bütünleşmektedir?
- Bir kavram hangi daha yüksek Anlam'ın tezahürüdür?
- Referans Noktası'na doğru yönelim nedir?

Piramit bu nedenle graph'ın alternatifi değildir.

> **Graph, Piramit'in yatay kesitlerinde yaşamaya devam eder.**

Her ontolojik seviyenin kendi semantic graph'ı bulunabilir.

```text
                         ●
                       Logos
                         │
                 ┌───────┴───────┐
                 │  Principles   │
                 └───────┬───────┘
                    ╱     │     ╲
                   ╱      │      ╲
              Archetypal Forms
             ↙ ↔ ↘    ↙ ↔ ↘    ↙ ↔ ↘
          ─────────────────────────────
                Domain Concepts
          ↔    ↗  ↘   ↔   ↗  ↘    ↔
        ───────────────────────────────
               Semantic Models
        ↔  ↔  ↔  ↔  ↔  ↔  ↔  ↔  ↔
      ─────────────────────────────────
                Observed Data
       •  •  •  •  •  •  •  •  •  •
```

Böylece:

**Horizontal Semantics**

> Bu şey başka hangi şeylerle ve nasıl ilişkilidir?

**Vertical Ontology**

> Bu şey hangi daha yüksek Anlam/Form'un tezahürüdür?

soruları birbirinden ayrılabilir.

---

## Ontolojik İlişki `is-a` Değildir

Dikey bağlantıyı klasik class hierarchy ile karıştırmamak gerekir.

Örneğin:

```text
for_statement
      ↑
   iteration
      ↑
  repetition
      ↑
    cycle
      ↑
Archetypal Form
      ↑
  Principle
```

Buradaki bağlantıların tamamı `is-a` değildir.

Bir `for_statement`, ontolojik anlamda `cycle`ın subclass'ı olmak zorunda değildir.

Bunun yerine:

> **`for_statement`****, belirli bir bağlam içerisinde Cycle anlam-formunun tezahürü olabilir.**

Dolayısıyla ontology sisteminin klasik ilişkilerin yanında bir **manifestation / instantiation / participation / derivation** türü dikey ilişki modeline ihtiyacı olabilir.

Bu ilişkinin kesin mahiyeti ayrıca araştırılmalıdır.

---

## İki Yönlü Hareket

Piramit iki yönde okunabilir.

### Keşif Yönü

```text
Observation
    ↓
Pattern
    ↓
Semantic Form
    ↓
Archetype
    ↓
Principle
```

Gözlemlerden hareketle daha sabit Anlam formları keşfedilir.

Ontology'nin bütün arketiplerinin başlangıçta bilindiği varsayılmaz. Gözlem, karşılaştırma ve örüntü keşfi yoluyla yeni ara formlar ortaya çıkarılabilir.

### Tezahür Yönü

```text
Principle
    ↓
Archetype
    ↓
Semantic Form
    ↓
Domain Concept
    ↓
Manifestation
```

Bu yönde ise yüksek ontolojik düzeylerdeki anlamların farklı domain'lerde hangi biçimlerde tezahür ettiği incelenir.

Böylelikle aynı yapı hem **bottom-up discovery** hem de **top-down interpretation** için kullanılabilir.

---

## Arketiplerin Konumu

Arketipler, İlkeler ile domain dünyası arasında bulunan **ara anlam formları** olarak düşünülebilir.

```text
                    İLKELER
                       │
                       │
                   ARKETİPLER
                 /     │      \
                /      │       \
             Döngü   Merkez    Akış
                \      │       /
                 \     │      /
                  DOMAIN FORMS
                       │
                    KAVRAMLAR
                       │
                     VERİ
```

Bu nedenle arketiplerin tamamının baştan bilinmesi gerekmeyebilir.

Semantic Observatory'nin görevlerinden biri, farklı domainlerde tekrar tekrar tezahür eden yapıları gözlemleyerek **Sabit Anlam Kalıplarını keşfetmek** olabilir.

---

## Semantic Observatory'nin Rolü

Semantic Observatory ontology'yi gerçekliğe dayatan bir sistem olmamalıdır.

Daha ziyade:

> **Tezahürleri gözlemleyerek onların işaret ettiği daha sabit anlam formlarını keşfetmeye çalışan bir sistem**

olarak düşünülebilir.

Bu nedenle sistem döngüsel olarak çalışabilir:

```text
Ontology
    ↓
Observation
    ↓
Pattern / Conflict
    ↓
Interpretation
    ↓
Ontology Proposal
    ↓
Validation
    ↓
Ontology Evolution
    └──────────────→ Observation
```

Ontology böylece statik bir `.ttl`, `.yaml` veya schema dosyası olmaktan çıkarak **yaşayan ve versioned bir semantic model** hâline gelir.

---

## Semantica'dan Alınabilecek Ontology Management İlkeleri

Semantica'nın ontology yaklaşımı bu modelin kendisi olmak zorunda değildir; fakat ontology'nin **yönetilmesi** konusunda güçlü teknik örnekler sunmaktadır.

Özellikle:

- ontology generation,
- class/property inference,
- formal schema generation,
- SHACL constraints,
- validation,
- ontology evaluation,
- cross-ontology alignment,
- versioning,
- diff,
- proposal/review/publish workflow,
- &#x20;health monitoring of the ontological model

gibi mekanizmalar Semantic Observatory için değerlendirilebilir.

Bu durumda Semantica'nın teknik yaklaşımı ile Ontology Pyramid arasında şöyle bir ayrım yapılabilir:

> **Semantica bize ontology'nin nasıl yönetilebileceğine dair yöntemler sağlayabilir; Ontology Pyramid ise ontology'nin hangi geometrik ve ontolojik yapıya sahip olması gerektiğini araştırır.**

---

## Ontological Level ve Ontological Orientation

Klasik ontology sistemlerine eklenmesi gereken iki temel kavram olabilir:

### Ontological Level

Bir kavramın Piramit'in hangi dikey seviyesinde bulunduğunu ifade eder.

Örneğin:

```text
Principle
Archetype
Semantic Form
Domain Concept
Instance
Observation / Data
```

Bu seviyelerin kesin sayısı ve isimleri henüz sabit kabul edilmemelidir.

### Ontological Orientation

Bir semantik nesnenin Referans'a doğru hangi dikey ilişkiler üzerinden bağlandığını ifade eder.

Böylece ontology management'ın temel sorusu yalnızca:

> Hangi node hangi node'a bağlı?

olmaktan çıkar.

Daha temel soru şudur:

> **Bir bilginin Piramit'teki doğru yeri neresidir ve onu Referans'a bağlayan dikey yol nedir?**

---

## Geometric Cohesion

Ontology Pyramid aynı zamanda **Geometric Cohesion** ilkesinin ontolojik ölçekte uygulanması olarak görülebilir:

> **Every semantic connection must be explicit, deterministic, and locally consistent with its neighboring connections.**

> Her semantik bağlantı açık, doğrulanabilir ve yerel kurallarla tutarlı olmalıdır; sistemin bütünlüğü bu bağlantıların bütünlüğünden doğar.

Fakat Piramit buna bir şart daha ekler:

**Yerel bağlantıların tutarlılığı, bütünün ontolojik yönelimiyle de uyumlu olmalıdır.**

Yatay graph düzgün olduğu hâlde dikey yönelim kaybolmuşsa sistem semantik olarak tutarlı fakat ontolojik olarak yönsüz olabilir.

---

## Piramit'in Labirenti

Referans Noktası'ndan kopulduğunda alt katmanların giderek genişleyen graph'ı bir **labirente** dönüşebilir.

Daha fazla veri, daha fazla node ve daha fazla edge bu problemi çözmez; aksine büyütebilir.

Bu nedenle bilgi sisteminin amacı yalnızca hafızayı büyütmek değildir.

Amaç:

> **çokluğu Referans'a bağlı bir bütünlük içerisinde muhafaza etmek**

olmalıdır.

Bu anlamda Piramit hem **Hafıza'nın geometrisi** hem de Hafıza içerisindeki Bilgi'ye yönelmenin haritası olarak düşünülebilir.

Semantic Observatory'nin Ontology Pyramid'i de bu nedenle yalnızca bir knowledge representation modeli değil; **veriden Bilgi'ye ve çokluktan Birlik'e yönelen bir semantic navigation architecture** olarak araştırılmalıdır.
