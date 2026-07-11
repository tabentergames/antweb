# TabX Frameless Kabuk Araştırması

Son güncelleme: 2026-07-08

## Amaç

F2.5 backlog'undaki frameless pencere kabuğu maddesi, doğrudan uygulama işi
değil araştırma dilimidir. Hedef, `FramelessWindowHint` ve özel başlık çubuğu
yaklaşımının TabX için ne zaman anlamlı olduğunu netleştirmektir.

## Kısa karar

Şu aşamada frameless kabuk uygulanmamalı. TabX'in önceliği çalışan tarayıcı
yüzeylerini ve F5/F6/F7 modüllerini büyütmek olmalı. Frameless pencere, özellikle
macOS'ta pencere sürükleme alanı, trafik ışıkları, tam ekran davranışı, native
menü beklentileri ve erişilebilirlik açısından küçük görünen ama geniş test
matrisi isteyen bir değişikliktir.

## Teknik notlar

- `Qt.WindowType.FramelessWindowHint` native başlık çubuğunu kaldırır; pencere
  taşıma, çift tıkla zoom, kenardan yeniden boyutlandırma ve platforma özgü
  kontrollerin bir kısmı uygulama tarafından tekrar ele alınmalıdır.
- macOS trafik ışıklarını taklit etmek yeterli değildir. Kullanıcılar sistem
  davranışlarını bekler: tam ekran, pencere menüsü, sürüklenebilir alanlar ve
  Mission Control uyumu.
- QtWebEngine içeriği ayrı GPU yüzeyinde çizildiği için pencere-seviyesi görsel
  efektler ve webview üstü etkileşimler dikkatli ayrılmalıdır. F2.5 snapshot
  kuralı korunur; webview'e opacity/transform uygulanmaz.
- Mevcut F2.6 rail'siz ve overlay panel kabuğu, frameless olmadan zaten daha
  temiz ve tam genişlikli bir yüzey sağlıyor.

## Önerilen koşullar

Frameless kabuk ancak şu koşullar sağlanırsa ayrı bir spike olarak açılmalı:

- F5 veya F7'de kullanıcıya dönük güçlü bir deneyim parçası tamamlanmış olmalı.
- macOS üzerinde manuel görsel test yapılabilecek gerçek ekran oturumu olmalı.
- Ayrı bir branch'te sadece pencere kabuğu denenmeli; sidebar, toolbar, sekme ve
  webview davranışları aynı değişiklikte refactor edilmemeli.
- Geri dönüş yolu basit olmalı: tek feature flag veya küçük bir pencere kurulum
  dalı ile native başlık çubuğuna dönülebilmeli.

## Gelecek spike kapsamı

1. Native başlık çubuğu açıkken mevcut F2.6 kabuğun ekran görüntüsünü referans al.
2. `FramelessWindowHint` ile minimum prototip oluştur.
3. Sürükleme alanı, yeniden boyutlandırma, tam ekran ve odak davranışını test et.
4. Webview, fan overlay, sol/sağ overlay panel ve context menu ile çakışma var mı
   doğrula.
5. Kazanç/karmaşıklık oranı net değilse değişikliği merge etme.
