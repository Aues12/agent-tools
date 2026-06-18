# Semantic Observatory – Faz Döngüsü, Semantic Ring ve Mananın Lokalizasyonu

## Temel Tez

Semantic Observatory'nin amacı yalnızca kodu görselleştirmek değildir.

Amaç:

> Kodun anlamını, teknik gerçekliğine uygun biçimde lokalize etmek.

Kod yalnızca AST düğümlerinden oluşmaz.

Kod:

* dönüşüm döngülerinden,
* anlam akışlarından,
* sabitleme ve hareket süreçlerinden,
* tekrar eden faz çevrimlerinden

oluşur.

---

# Event Horizon

Sistemin en temel katmanı:

0 ↔ 1

Örnek ikilikler:

* Var ↔ Yok
* Aktif ↔ Pasif
* Hareket ↔ Sabitlik
* Geçiyor ↔ Geçmiyor
* Belirlenmiş ↔ Belirlenmemiş

Bu ikilik, tüm sistemin temel eşiğidir.

---

# Dört Faz Döngüsü

Toprak

* Ürün
* Sabitlenen form
* Çıktı
* Alınan malzeme

Ateş

* Dönüşüm
* İşlem
* Yeni temsilin oluşmasını sağlayan faaliyet

Hava

* Geçici hafıza
* Geçici sabitleme
* Ara temsil

Su

* Akış
* Yazım
* Analiz
* İşleme faaliyeti

---

# Zorunlu Faz Çevrimi

Sistemin temel çevrimi:

Toprak → Ateş → Hava → Su → Toprak

Bu sıralama korunmalıdır.

İstisnai sınır durumlar bulunabilir, ancak genel ilke budur.

Bu çevrim:

* su döngüsü,
* enerji döngüsü,
* bilgi işleme süreçleri,
* programlama faaliyetleri

ile benzer biçimde düşünülebilir.

---

# parse_file Referans Örneği

```python
def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
```

Faz analizi:

path
→ Toprak

read_file(path)
→ Ateş

text
→ Hava

ast.parse(text)
→ Su

tree
→ Toprak

Dolayısıyla:

Toprak
↓
Ateş
↓
Hava
↓
Su
↓
Toprak

çevrimi oluşur.

Bu örnek referans örnek olarak korunmalıdır.

---

# Fraktal Faz İlkesi

Her varlık:

1. Kendi içinde faz çevrimi taşıyabilir.
2. Üst ölçekte baskın bir faza sahip olabilir.

Örnek:

parse_file()

İç ölçekte:

Toprak → Ateş → Hava → Su → Toprak

Üst ölçekte:

Su

çünkü sistem içerisindeki ana görevi analizdir.

Bu ilke:

* statement
* function
* class
* module
* package
* system

ölçeklerinin tamamında geçerlidir.

---

# Semantic Ring

Bazı yapılar baskın bir faz taşımaz.

Örnekler:

* main()
* runner()
* workflow()
* scheduler()
* event_loop()
* pipeline()

Bu yapıların görevi:

Bir faz olmak değil,

fazlar arasındaki dolaşımı kurmak ve çevrimi tamamlamaktır.

Bu nedenle bunlar:

Semantic Ring

olarak adlandırılabilir.

Semantic Ring:

* fazları birbirine bağlar,
* çevrimi kapatır,
* akışı aktive eder.

Bir program çalıştırıldığında:

Semantic Ring kapanır,

ve bilgi/enerji/mana akışı gerçekleşir.

---

# Semantic Seal

Semantic Ring'in merkezinde yer alan anlam çekirdeği:

Semantic Seal

olarak adlandırılabilir.

Ring:

hareketi temsil eder.

Seal:

hareketin merkezindeki fikri temsil eder.

Örnek:

parse_file()

Semantic Ring:
dosya → okuma → geçici temsil → analiz → AST

Semantic Seal:
"metni yapıya dönüştürmek"

Semantic Seal, bir yapının veya dönüşüm çevriminin merkezinde bulunan ve ona kimliğini veren anlam çekirdeğidir.

---

# Geometri İlkesi

Yapısal geometri ile faz geometrisi birbirinden bağımsız değildir.

İkisi aynı düzenin farklı ölçeklerdeki tezahürleridir.

AST
↓
Call Graph
↓
Semantic Geometry

ile

Event Horizon
↓
Faz Çevrimi
↓
Semantic Ring

fraktal olarak tekabül eder.

---

# Semantic Observatory'nin Temel Görevi

Kodun sözdizimini göstermek değil,

kodun:

* dönüşüm döngülerini,
* faz çevrimlerini,
* anlam akışlarını,
* Semantic Ring yapılarını,
* Semantic Seal merkezlerini

görünür hale getirmektir.

Bu yaklaşım:

Mananın Lokalizasyonu

olarak adlandırılabilir.
