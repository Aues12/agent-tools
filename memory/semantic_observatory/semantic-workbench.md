# Semantic Workbench – Role ve Epistemik Katman Ayrımı

## Temel Gözlem

Semantic Workbench içinde teknik roller ile epistemik roller birbirine karıştırılmamalıdır.

Teknik roller, bir yazılım bileşeninin sistem içinde ne yaptığını tanımlar.

Örnek teknik roller:

* Parser
* Builder
* Transformer
* Validator
* Locator
* Explorer
* Aggregator
* Renderer
* Executor

Bu roller domain-specific olabilir.

Örneğin bir derleyicide (compiler):

* Parser
* Visitor
* Transformer

rolleri yaygın olabilir.

Bir web uygulamasında:

* Controller
* Service
* Repository

rolleri yaygın olabilir.

Bir optimizasyon sisteminde:

* Solver
* Evaluator
* Scheduler

rolleri görülebilir.

Dolayısıyla teknik roller projeden projeye değişebilir.

---

## Epistemik Katman

Epistemik katman daha üst seviyeli ve daha evrenseldir.

Bir bilgi edinme veya problem çözme sürecindeki temel hareketleri tanımlar.

Önerilen epistemik katmanlar:

1. Discovery (Görmek / Keşfetmek)
2. Understanding (Anlamak)
3. Transformation (Dönüştürmek)
4. Manifestation (Gerçekleştirmek / Eylemek)

Bu katmanlar teknik rollerden bağımsızdır.

Örneğin:

Role: Locator
Phase: Discovery

Role: Parser
Phase: Understanding

Role: Transformer
Phase: Transformation

Role: Builder
Phase: Manifestation

şeklinde eşleşebilir.

---

## Tasarım İlkesi

Sembolik sistemler teknik gerçekliğin yerine geçmemelidir.

Sembolik sistemlerin amacı:

* Hatırlamayı kolaylaştırmak
* Navigasyonu kolaylaştırmak
* Örüntüleri görünür kılmak

olmalıdır.

Dolayısıyla:

Epistemik Katman = Harita

Teknik Roller = Arazi

şeklinde düşünülebilir.

Harita arazinin yerine geçmez; yalnızca arazide yön bulmayı kolaylaştırır.

---

## Semantic Card Önerisi

Bir kart iki farklı sınıflandırma taşıyabilir:

Type:
Function

Role:
Transformer

Phase:
Transformation

Depth:
2

Bu sayede:

* Teknik görev
* Epistemik bağlam
* Yapısal konum

aynı anda görülebilir.

---

## Uzun Vadeli Hedef

Semantic Workbench yalnızca kod navigasyonu değil, genel bilgi navigasyonu için bir altyapı olabilir.

Bu durumda:

* Kod
* Dokümanlar
* Araştırma notları
* Investigation Memory kayıtları
* Optimizasyon modelleri

aynı epistemik çerçeve içinde temsil edilebilir.
