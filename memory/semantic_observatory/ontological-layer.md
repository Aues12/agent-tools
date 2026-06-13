# Semantic Workbench – Ontoloji → Epistemoloji → Teknik → Somut Katmanlar

## Temel Gözlem

Semantic Workbench yalnızca bir kod navigasyon aracı değildir.

Daha genel anlamda, bilgi içerisinde yön bulma ve anlamı yerelleştirme (localize etme) problemine yönelik bir mimari araştırmadır.

Bu nedenle sistem farklı soyutlama seviyelerinde düşünülmelidir.

---

# 1. Ontolojik Katman

Bu katman en üst seviyedeki ilkeleri ifade eder.

Burada amaç belirli teknik rolleri değil, bilgi ve varlık ile ilişki kurmanın temel yönlerini anlamaktır.

## Hayy (Akış)

* Hareket
* Potansiyel
* Değişim
* Keşif
* Üretkenlik

Hayy yönü yeni yolların açılması ve anlamın ortaya çıkışı ile ilişkilidir.

## Kayyum (Form)

* Düzen
* Stabilite
* Yapı
* Koruma
* Süreklilik

Kayyum yönü ortaya çıkan anlamın korunması ve biçim kazanması ile ilişkilidir.

---

# 2. Epistemik Katman

Bu katman bilgi ile çalışma sürecini tanımlar.

Ontolojik ilkelerin bilgi edinme sürecindeki görünümüdür.

## Discovery

Görmek.

* Aramak
* Keşfetmek
* Fark etmek

## Understanding

Anlamak.

* Yorumlamak
* Bağlamlandırmak
* Kavramlar arasında ilişki kurmak

## Transformation

Dönüştürmek.

* Yeniden düzenlemek
* Sıkıştırmak
* Haritalamak
* Çevirmek

## Manifestation

Gerçekleştirmek.

* Üretmek
* İnşa etmek
* Uygulamak
* Dışsallaştırmak

---

# 3. Teknik Katman

Bu katman belirli yazılım rollerini içerir.

Bu roller proje veya alan özelinde değişebilir.

Örnek roller:

* Parser
* Builder
* Transformer
* Validator
* Locator
* Explorer
* Aggregator
* Renderer
* Executor

Bu roller epistemik katmanların altında kümelenebilir.

Örnek:

Discovery

* Explorer
* Locator

Understanding

* Parser
* Analyzer
* Validator

Transformation

* Transformer
* Aggregator

Manifestation

* Builder
* Renderer
* Executor

---

# 4. Somut Katman

Bu katman kullanıcının doğrudan gördüğü nesneleri içerir.

Örnek:

* Kod
* Doküman
* Semantic Card
* Investigation Memory
* Diagnostic Record
* Görev
* Rapor

Bu katman teknik rollerin somut çıktılarından oluşur.

---

# Tasarım İlkesi

Role ve Phase aynı şey değildir.

Role:
"Ne yapıyorum?"

sorusuna cevap verir.

Phase:
"Bilgi edinme sürecinin hangi aşamasındayım?"

sorusuna cevap verir.

Birden fazla Role aynı Phase altında bulunabilir.

Bu nedenle:

Role = Teknik sınıflandırma

Phase = Epistemik sınıflandırma

olarak ele alınmalıdır.

---

# Zanaatkâr'ın İki Eli

Bu yapı, "Zanaatkâr'ın İki Eli" düşüncesinin teknik bir yorumu olarak görülebilir.

Hayy yönü:

* Akış
* Keşif
* Sezgi
* Açılım

Kayyum yönü:

* Form
* Düzen
* Prosedür
* Stabilizasyon

Semantic Workbench'in amacı bu iki yön arasında denge kurmaktır.

Ne tamamen serbest akış,
ne de tamamen katı yapı.

Amaç anlamın ortaya çıkmasını ve korunmasını birlikte mümkün kılan bir navigasyon mimarisi kurmaktır.
