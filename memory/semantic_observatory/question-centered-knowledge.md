# Soru Merkezli Bilgi Çıkarımı ve Sınırlı Hafıza

Durum: Experimental — mimari araştırma notu. Buradaki retrieval, bütçe ve
hafıza yönetimi davranışları mevcut araçların uygulanmış özellikleri değildir.

## Yönelim

Semantic Observatory, kaynaklardan anlamlı yapılar çıkaran, bu yapılar içinde
yön bulmayı ve edinilen anlayışı yeniden kullanmayı mümkün kılan bir bilgi
erişim, yönetim ve sınıflandırma sistemi olarak gelişebilir.

Çıkarımın başlangıcı belirli bir sorudur:

> Bu soruyu cevaplamak için kaynağın hangi ilişkilerini görünür kılmalıyım?

Aynı kaynaktan işleyiş grafiği, argüman haritası, kavram ağı, etki analizi veya
öğrenme yolu çıkarılabilir. Bunlar farklı sorulara hizmet eden lokalizasyonlardır.
Bir temsilin sınırı, nesnenin anlamının sınırı değildir.

Soru dikkati yönlendirir; cevabı baştan belirlememelidir. Kaynak sorunun yanlış
kurulduğunu gösterebilir. Beklenmeyen bir gözlem, kapsamı bilinçli olarak yeniden
belirlemeye veya ayrı bir araştırma açmaya neden olabilir.

## Referans örnek: BookBarcode

[BookBarcode işleyiş grafiği](../../agent-playground/semantic_graph/bookbarcode_workflow_dag.json),
“bu sistem nasıl çalışıyor?” sorusuna yönelik bir agent üretimidir. Girdi,
doğrulama, ortak durum, geometri, render ve çıktı ilişkilerini seçerek kodun
çalışma mantığını görünür kılar. Bir düğüm birden çok kaynak parçasını
birleştirebilir; her fonksiyonun ayrı düğüm olması gerekmez.

Agent anlamı seçer, ilişkilendirir ve adlandırır. `semantic_graph` kimlikleri,
kenar uçlarının bütünlüğünü ve kaydı yönetir. Deterministik analizler agent'ın
incelemesine dayanak sağlayabilir; yorumlama faaliyeti ayrıca korunur.

Grafiğin mevcut `attributes` alanları boştur; kaynak dayanakları henüz bu
alanlarda kayıtlı değildir. Adındaki DAG ifadesi de aracın DAG doğrulaması
uyguladığı anlamına gelmez. Örnek bir açıklama haritasıdır; doğrudan yürütülebilir
bir workflow sözleşmesi olarak kabul edilmemelidir.

## Birbirini tamamlayan dört yetenek

### 1. Kaynağa erişmek

İlgili dosyayı, pasajı, fonksiyonu veya kaydı bulmak; ihtiyaç oldukça ayrıntıya
inmek. İlk erişim, kaynağın tamamını aktif bağlama almak zorunda değildir.
Arama sonucu önce kimlik, kısa açıklama, konum ve uygunluk gerekçesi sunabilir.

Soru hangi bölümün okunacağını belirler. Seçilen bölümün bağlamını değiştiren
öncüller, istisnalar veya komşu ifadeler de gerektiğinde açılır.

### 2. Anlamlı bir yapı kurmak

Agent kavramları, sorumlulukları, aşamaları ve ilişkileri önerir; araç kaydeder.
Temsilin kapsamı soruya göre seçilir. Çıkarım, seçme ve sıkıştırma içerdiğinden
kaynağa geri dönüş yolu korunmalıdır.

Gelecekteki bir bilgi çıkarımı skill'i şu yöntemi taşıyabilir:

1. Soruyu ve beklenen kullanımını belirle.
2. Kaynak kapsamını ve çalışma bütçesini seç.
3. İlgili parçaları incele; gerekli ilişkileri kur.
4. Önemli düğüm ve kenarları kaynak referanslarıyla ilişkilendir.
5. Temsili kaynakla karşılaştır; belirsizlikleri ve dışarıda kalanları kaydet.
6. Soruyu yeterince cevaplayan sınırlı bir sonuç üret; devam işlerini ayır.

Bu not yeni bir skill uygulamaz; başarılı çıkarımların yöntemini koruma yönünü
tanımlar.

### 3. Birikmiş bilgi içinde yeniden bulmak

Erişim, yalnızca isim eşleştirmesiyle sınırlı kalmamalıdır. Örneğin:

> Önce geçici çıktı üret, doğrula, sonra yayınla örüntüsünü başka nerede gördük?

Bu soru tekil bir uygulamadan genel örüntüye, oradan başka uygulamalara geçer.
Önerilen tekabülün hangi ortak ilişkilere dayandığı açıklanmalıdır; benzer
etiketler tek başına eşdeğerlik göstermez.

Önce sınırlı aday listesi, sonra seçilen adayların yerel ilişkileri, ardından
kaynak ayrıntısı açılır. Arama tek seferde bütün bilgi ağını yüklememelidir.

### 4. Bilgiyi yaşatmak

Kaynak değiştiğinde ilişkili temsilin gözden geçirilmesi gerekir. Eski yorum,
yeni yorum ve değişme gerekçesi ilişkilendirilir. Değişiklik bütün hafızayı
baştan kurmayı gerektirmemeli; mümkün olduğunda etkilenen alan ele alınmalıdır.

Koruma, her şeyi süresiz saklamak anlamına gelmez. Tekrar kullanılan anlayış
kararlı biçim kazanır; geçici çalışma malzemesi ayıklanır. Kaynak sürümü veya
analiz yöntemi bilinmiyorsa güncellik varsayılmamalıdır.

Bu dört yetenek katı bir sıra veya yeni bir dört-element eşlemesi değildir.
Bir yapı kurarken kaynağa dönülebilir; eski bir örüntü yeni soruyu değiştirebilir.

## Progressive disclosure: görünüm ve bağlam birlikte sınırlanmalı

Aşamalı açılım hem insanın dikkatine hem agent'ın context window'una uygulanır.
Arayüzde kapalı duran bir panelin tüm içeriğini agent'a göndermek bu ilkeyi
karşılamaz. Açılım, veri getirme ve tool yanıtı düzeyinde de gerçekleşmelidir.

| Katman | Açılan bilgi | İlerlemenin nedeni |
|---|---|---|
| Dizin | Kimlik, başlık, kısa açıklama, kapsam | İlgili alanı seçmek |
| Kart | Soruyu cevaplayan öz, temel ilişkiler, belirsizlik | Yerel anlayış kurmak |
| Yerel görünüm | Seçili komşular veya süreç aşamaları | Bir ilişkiyi takip etmek |
| Dayanak | Kaynak pasajı/kod, sürüm, çıkarım gerekçesi | İddiayı incelemek |

Her açılım bir sonraki karar için gereken miktarı getirmelidir. Büyük sonuçlar
sayfalanmalı veya daraltılmalıdır. Özetin neleri dışarıda bıraktığı ve ayrıntının
nasıl geri çağrılacağı anlaşılır kalmalıdır. Sıkıştırma, kritik koşulları ve
çelişkileri sessizce ortadan kaldırmamalıdır.

## Aktif bağlam ile kalıcı hafıza

Üç ayrı sorumluluk önerilir:

* **Aktif çalışma bağlamı:** mevcut soru, seçilen dayanaklar, alınan kararlar ve
  sıradaki adım. Her turda bütün geçmişi taşımaz.
* **Erişim dizini:** hangi bilginin nerede ve hangi kapsamda bulunduğunu gösteren
  kısa kayıtlar. Dizin de bölümlenip sayfalanabilir; tamamı bağlama alınmaz.
* **Kalıcı bilgi alanları:** yeniden kullanılabilir kartlar, yerel grafikler,
  kaynak referansları ve gerekli revizyonlar. Bunlar da saklama politikasıyla
  sınırlıdır.

Context window sınırı ile depolama sınırı farklıdır. Daha büyük disk, daha çok
bilgiyi tek seferde anlayabilmeyi sağlamaz. Daha kısa bir prompt da kontrolsüz
büyüyen kalıcı hafıza sorununu çözmez.

Aktif bağlamdan çıkan bir kayıt silinmiş sayılmaz; kimliği ve erişim yolu ile
yeniden getirilebilir. Arşivden gerçekten kaldırılan bir kaynağın artık
getirilemeyeceği ise açıkça belirtilmelidir.

## Bütçe ve durma koşulları

Her araştırma için duruma göre sınırlı bir çalışma sözleşmesi kurulabilir:

* hangi soru, alan ve kaynak sürümleri ele alınıyor;
* en fazla kaç aday, kaynak parçası ve ilişki açılacak;
* yerel grafiğin düğüm/kenar ve gezinme derinliği sınırları;
* bağlamda dayanaklara ayrılan pay ve cevap/akıl yürütme için bırakılan alan;
* hangi sonuç yeterli sayılacak ve ne zaman devam başka bir araştırmaya ayrılacak.

Sabit bir evrensel token sayısı önerilmez. Bütçe, modelin erişilebilir bağlamına,
göreve ve mevcut araçların döndürdüğü veri hacmine göre seçilir.

Soru cevaplandığında veya bütçe dolduğunda genişleme durur. Bütçenin dolması
sorunun cevaplandığı anlamına gelmez. Sonuç; bulunanları, açık kalan soruları,
incelenmeyen alanları ve devam için gereken sınırlı sonraki adımı kaydeder.

Bağlam devrinde bir çalışma özeti tutulabilir: soru, kapsam, kararlar, dayanak
kimlikleri, belirsizlikler ve sıradaki adım. Özet kaynakların yerine geçmez;
önemli iddialar ihtiyaç halinde yeniden açılır.

## Sonsuz büyüme yerine sınırlı bilgi alanları

Bütün bilgiyi sürekli genişleyen tek bir grafikte toplamak zorunlu değildir.
Her araştırma kendi sorusu etrafında sınırlı bir alan oluşturabilir. Alanlar
birbirlerine kimlik ve kaynak bağlantıları üzerinden açılır; başka alanın tüm
alt yapısı kopyalanmaz. Bir düğümün kimliği alanlar arasında taşınırken
`graph_id` ve yerel düğüm kimliği birlikte kullanılmalıdır.

Yeni kalıcı kayıt için gerekçe aranır: yeniden kullanım, önemli bir karar,
yeni bir ilişki veya mevcut anlayışın düzeltmesi. Her arama sonucu ve geçici
LLM ifadesi otomatik olarak hafızaya yükseltilmemelidir.

Düzenli bakımda tekrarlar birleştirilir, geçersizleşmiş kayıtlar işaretlenir,
yerini yenisine bırakmış içerik arşivlenir; saklama bütçesine göre değeri düşük
geçici içerik kaldırılabilir. Arşiv de sınırsız bir birikim alanı değildir.
Birleştirme veya kaldırma, bağlı referansları sessizce bozmamalıdır; yönlendirme
ya da kaldırılma kaydı bırakılmalıdır. Bunlar ileride açık yan-etki sözleşmeleri
olan araçlarla uygulanacak davranışlardır.

Sınıflandırma sözlüğü de deneyimle gelişir. Yeni `kind` değerleri önerilebilir;
tekrar eden adlandırmaların anlamı, bağlamı ve birbirleriyle ilişkisi zamanla
netleştirilir. Her yeni ifade için yeni ve kalıcı bir kategori açmak gerekmez.

Hayy yönü keşfi ve yeni bağlantıları mümkün kılar. Kayyum yönü bunların elde
tutulabilir, sınırları bilinen ve yeniden ziyaret edilebilir biçim kazanmasını
sağlar. Bir alanın tamamlanması onun mutlaklaşması değildir; başka bir soruda
yeniden açılabilir.

## Geliştirme ve değerlendirme yönü

İlk deney, BookBarcode haritasına kaynak bağları eklemek, çıkarım yöntemini
tekrar etmek ve aynı yaklaşımı bir epistemoloji yazısında denemek olabilir.

Başarı daha fazla düğüm üretmekle ölçülmemelidir. Şunlar incelenebilir:

* İlgili anlayış, sınırlı okumayla yeniden bulunabiliyor mu?
* Seçilen ilişkiler kaynaklarına kadar izlenebiliyor mu?
* Özet gerekli koşulları ve belirsizlikleri koruyor mu?
* Yeniden kullanım gerçekten okumayı azaltırken cevabın yeterliliğini koruyor mu?
* Kaynak değişikliği ilgili temsile yansıtılabiliyor mu?
* Bütçe sonunda tamamlanma ile açık iş birbirinden ayırt ediliyor mu?

İlişkili notlar: [Localization](localization.md), [Semantic Cards](semantic-cards.md),
[Quest Tree](quest-tree.md), [Epistemic Grounding](epistemic-grounding.md).
