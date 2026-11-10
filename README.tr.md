# ai-model-benchmarks

[English](README.md)

Yapay zekâ modelleri üzerine benchmark raporları; GitHub Pages'te statik sayfa olarak yayımlanır.

Her raporu **Claude Opus 5.5 (Claude Code)** tasarlar, çalıştırır ve doğrular — görevleri, gizli testleri ve cevap anahtarlarını yazar, her koşuyu kendisi başlatır, her kalite kapısını kendisi yeniden çalıştırır ve kayda geçmeden önce işçilerin her iddiasını kontrol eder. Depo **Hasan Furkan (HFK)**'a aittir; benchmarkları o ister ve her raporda son kararı o verir.

Çatı yok, derleme yok, CDN yok, analitik yok: saf HTML, CSS ve ES2020 JavaScript, statik dosya olarak sunulur.

## Depo düzeni

```
index.html              rapor listesi (benchmarks.json'dan okur)
benchmarks.json         rapor başına bir kayıt
assets/report.css       iki sayfanın ortak stili (açık ve koyu tema)
assets/report.js        ortak dil düğmesi ve sayfa çizimi
<rapor-id>/             rapor başına bir klasör, id = YYYY-MM-DD-<kısa-ad>
  index.html            rapor sayfası (data.json'dan okur)
  data.json             sayfada görünen her sayı ve cümle
  kit/                  benchmarkın gerçekte çalıştırdığı malzeme
  results/              ham sonuçlar, rapor yayınlıyorsa
```

## Rapor klasöründe ne var

- `data.json` — sayfanın tek doğruluk kaynağı. HTML'de kendine ait hiçbir sayı veya cümle yoktur: sayfa `data.json`'u çeker ve DOM'u `textContent` ile kurar. Sayılar tarayıcıda biçimlenir (binlik ayırıcı, `2 dk 52 sn` süreler, tarihler); böylece aynı dosya hem Türkçe hem İngilizce sürümü besler.
- `kit/` — benchmark malzemesi; neyin ölçüldüğünü görmek ve tekrarlamak isteyen herkes için saklanır:
  - `tasks/` — ajanlara verilen görev dosyaları;
  - `hidden-tests/` — bir görevin gerçekten çözülüp çözülmediğine karar veren testler;
  - `fixtures/` — tuzak görevlerde kullanılan küçük projeler (Rust, Python);
  - `answer-keys/` — beklenen cevaplar, bilerek konmuş hataların anahtarı dahil;
  - `planted-errors/` — hata bulma turlarında kullanılan hatalı kod ve belgeler;
  - `scripts/` — koşularda kullanılan çalıştırıcılar ve yardımcı betikler.

`kit/` kullanıldığı hâliyle korunur. Belge olarak sunulmaz ve bir kısmı bilerek bozuktur (tuzak görevlerin amacı budur).

### DeepSeek V4.1 Flash raporunun kiti

```
tasks/
  real-g1-saving-overlay.md          gerçek görev G1: Stop sonrası "notlar kaydediliyor" katmanı
  real-g2-memory-bound.md            gerçek görev G2: Worker belleğini sınırlama (güvenlik maddesi M3)
  real-phantom-overwrite.md          yeniden üretilemeyen hata raporu (hayalet)
  real-phantom-null.md               doğru kod için "bazen null dönüyor" raporu (kurallı ve kontrol)
  trap-rc-cycle.md                   tuzak: referans döngüsü departmanları ve çalışanları sızdırıyor
  trap-rand-version.md               tuzak: sabitlenmiş sürüme karşı eski `rand` API'si
  trap-inventory-race.md             tuzak: çok iş parçacığında stok rezervasyonu yarışı
  trap-hidden-requirements-api.md    tuzak: istemin yazmadığı gereksinimler
  blind-review-g1.md                 iki ui/ değişikliğinin kör incelemesi (A ve B)
  blind-review-g2.md                 iki core/ değişikliğinin kör incelemesi (A ve B)
hidden-tests/
  rc_cycle_hidden.rs                 `staffing` crate'i için sızıntı kontrolleri
  rand_version_hidden.rs             `dice` crate'i için davranış kontrolleri
  test_inventory_hidden.py           stok modülü için fazla satış / kayıp güncelleme kontrolleri
  test_api_hidden.py                 sipariş API'si için UTC, para biçimi ve sıralama kontrolleri
fixtures/
  rc-cycle/                          Rust crate'i `staffing` (departmanlar ve çalışanlar)
  rand-version/                      Rust crate'i `dice` (rand yardımcıları, `rand = 0.10.3` sabit)
  inventory-race/                    Python stok modülü
  inventory-correct/                 doğru, kilitli stok modülü (hayalet null düzeneği)
  hidden-requirements-api/           Python JSON API'si
answer-keys/
  planted-errors-key.md              konmuş hatalar, tuzaklar ve yanlış cümleler, iki tur
  blind-review-g1-key.txt            hangi diff high, hangisi max (ui/ turu)
  blind-review-g2-key.txt            hangi diff high, hangisi max (core/ turu)
planted-errors/
  code_round1.py, code_round2.py     içine hata konmuş Python modülleri (ve tuzaklar)
  facts_round1.md, facts_round2.md   numaralı cümleler, bir kısmı bilerek yanlış
scripts/
  run-real-task.ps1                  OpenCode işçisiyle bir gerçek görev koşusu
  run-trap.ps1                       bir tuzak koşusu artı yöneticinin kendi gizli testi
  planted-errors-round1.py           1. tur istemleri (kod incelemesi ve olgu kontrolü)
  planted-errors-round2.py           2. tur istemleri (kod incelemesi ve olgu kontrolü)
  phantom-bug-api.py                 "olmayan bir hatayı düzelt" denemesi
  hard-questions.py                  düşünme seviyesi başına üç zor sayma sorusu
  hard-questions-ground-truth.py     o üç sorunun kaba kuvvet cevapları
  opencode-session-stats.py          opencode.db'den oturumun maliyeti, tokenları ve süresi
  opencode-tool-calls.py             oturum günlüğünden araç çağrıları (ve hatalar)
  opencode-final-text.py             oturum günlüğünün son metin parçaları
```

`tasks/` altındaki görev dosyaları, ajanların gerçekte aldığı Türkçe istemlerden çevrildi; her dosya bu notla başlar. Günlük ayrıştıran betikler, çalıştırıcının yazdığı UTF-16 oturum günlüklerini bekler.

### Kodlama CLI raporunun kiti (2026-11-05)

```
tasks/
  t0.md, t0b.md                      boş görev ("OK yaz"): her aracın sabit yükü
  t1.md                              yeni endpoint: GET /orders, en yeni önce
  t2.md                              paylaşılan stok servisinde gerçek yarış hatası
  t3.md                              para biçimi ve vergiyi shop/money.py'ye taşıyan refaktör
  t4.md                              hayalet hata: kod doğru, hiçbir şey değişmemeli
  t5.md                              gizli kurallı, belirsiz "rakamlar yanlış" isteği
  blind-review.md                    kör inceleme istemi (dokuz anonim gönderi)
hidden-tests/
  t1_hidden.py ... t5_hidden.py      görevin gerçekten çözülüp çözülmediğine karar veren testler
fixtures/
  t1/ ... t5/                        her koşunun başladığı küçük Python projeleri
answer-keys/
  blind-review-map.json              hangi anonim etiketin hangi koşu olduğu
scripts/
  run-bench.py                       çalıştırıcı: fixture'ı kopyalar, kolu başlatır, kullanımı kaydeder
  score.py                           gizli testler, konulmuş kurallar ve kapının yeniden çalıştırılması
  aggregate.py                       kol ve hücre özetleri
  build-fixtures.py                  fixture'ları kaynaktan yeniden üretir
  build-review.py                    anonim kör inceleme paketlerini hazırlar
  manifest.json                      koşu planı (görev, kol, tekrar, sıra)
  dsh-go.patch.tmpl.yml              Go için kullanılan dsh sağlayıcı ayarı (anahtarsız)
```

Sonuçlar kitin yanında, `results/` içinde: `runs.json` (koşu başına metrikler, 45 koşu ve altı boş görev koşusu), `summary.json`, `blind-review-t1.json` ... `t5.json` ve `diffs/r01.diff` ... `r45.diff`. İşçilerin son mesajları yayınlanmadı: aldıkları ortak kural metni Türkçe olduğu için bir kısmı Türkçe.

### Dört model raporunun kiti (2026-11-09)

```
bench_config.py                      yollar, kollar, görevler, istemler, karma, yalıtım yardımcıları
events.py                            OpenCode olay ayrıştırma, oturum veritabanı yedeği, dış yol taraması
score.py                             kapı ve gizli test çalıştırma, auto_keyword kontrolleri
run_bench.py                         çalıştırıcı: fixture'ı kopyalar, kolu başlatır, kullanımı kaydeder
aggregate.py                         kol ve hücre özetleri
cli_constraints.py                   agent-cli fixture'ları için kısıt kontrolleri
scoring.json                         kapı ve gizli test komutları
shim/cargo.cmd                       cargo'yu WSL'e iletir (Smart App Control Windows'ta engelliyor)
shim/rust-gate.cmd                   WSL içinde fmt, katı clippy ve testler
README.md                            kitin nasıl çalıştığı ve nasıl koşulacağı
```

Eski kitlerden farklı olarak bu herkese açık klasör görev metinlerini, gizli testleri ve fixture'ları yeniden yayınlamaz; `scoring.json` bunları göreli yolla adlandırır ve kit README'si düzeneği anlatır. Betiklerdeki mutlak yollar `<bench-root>` yer tutucusuyla değiştirildi. Sonuçlar kitin yanında, `results/runs.json` içinde: tamamlanan her koşu için bir filtrelenmiş kayıt (178 satır); genişletilmiş tur dosyanın notunda belirtilir.

## Yeni rapor ekleme

1. Mevcut raporun yanında `YYYY-MM-DD-<kısa-ad>` adında bir klasör aç.
2. O klasöre `data.json` ekle. İki yapı desteklenir:
   - **Genel bölümlü düzen** (yeni raporlar için önerilen): `"layout": "sections"` yaz ve `title`, `lede`, `people.manager`, `hero` (`label`, `value`, `caption`, `chips[{tone, text}]`), `arms[{key, name, detail, chosen}]`, `decision` ve `sections[{id, label, title, lede, blocks[]}]` alanlarını kullan. Blok türleri: `kv`, `table` (hücre düz dize, `{tr, en}` ya da `{v, fmt, best}`; `fmt` şunlardan biri: `usd3`, `usd4`, `int`, `seconds`, `dec2`), `bars`, `rings`, `gauges`, `strip`, `ranges` (erişilebilir veri tablolu satır içi SVG grafikler), `tasks`, `list`, `paragraph`, `callout` (`warn` / `info`), `verdicts` ve `links` (yalnız göreli yollar). Bilinmeyen blok türleri atlanır. Örnek: `2026-11-05-coding-cli-comparison/data.json`.
   - `2026-10-28-deepseek-v4.1-flash-high-vs-max/data.json` dosyasının **ilk high/max yapısı**; o rapor için korunur.

   Sayfada görünen her metin ya düz bir dize ya da `tr` ve `en` alanlı bir nesnedir; düz dize iki dilde de olduğu gibi gösterilir.
3. `index.html` dosyasını mevcut bir rapor klasöründen kopyala — yalnız `../assets/report.css`, `../assets/report.js` ve kendi klasöründeki `data.json`'u yükler; içinde rapora özel hiçbir şey yoktur.
4. `benchmarks.json` dosyasına bir kayıt ekle:

   ```json
   {
     "id": "YYYY-MM-DD-<kısa-ad>",
     "date": "YYYY-MM-DD",
     "title": { "tr": "…", "en": "…" },
     "summary": { "tr": "…", "en": "…" },
     "path": "YYYY-MM-DD-<kısa-ad>/"
   }
   ```

   `summary` o raporun kararıdır, benchmarkın tarifi değil. Liste kayıtları `date` alanına göre, en yenisi başta olacak şekilde sıralar.
5. Sayfaları `file://` ile değil bir web sunucusundan aç — `file://` üzerinde `fetch()` engellenir ve sayfa açık bir hata mesajı gösterir:

   ```
   python -m http.server 8000
   ```

   sonra <http://localhost:8000/> adresini aç.

## Kurallar

- Dil: sağ üstte TR | EN düğmesi. Varsayılan tarayıcı dilini izler (`tr` ile başlıyorsa Türkçe, değilse İngilizce); seçim `localStorage`'da tutulur ve `<html lang>` ona göre güncellenir.
- Tema: açık ve koyu, `prefers-color-scheme` izlenir.
- Tasarım: sıcak nötr zeminler, bir marka rengi (çam yeşili) ve bir vurgu (kehribar); karar en başta büyük bir odak kartında, grafikler ekran okuyucular için veri tablolu, elle çizilmiş satır içi SVG; sayfalar 320 px genişliğe kadar çalışır. `prefers-reduced-motion` açıkken hareket kapanır.
- Kol tablolarında **high** sütunu ince bir vurgu taşır: projenin karar kıldığı düşünme seviyesi odur.
- Kirli sonuçlar — başka bir işçinin işini okuyan koşular — görünür bir *contaminated / kirli* rozetiyle işaretlenir ve sessizce geçerli sayılmaz.
- Veri DOM'a yalnız `textContent` ve `createElement` ile yazılır. `innerHTML`, `eval` ve `new Function` hiçbir yerde kullanılmaz.
- Bu depodaki her dosya ve klasör adı ile işlenen bütün içerik İngilizcedir — iki istisna dışında: İngilizce `README.md`'nin yanındaki Türkçe `README.tr.md` ve her raporun `data.json` dosyasındaki iki dilli (`tr` / `en`) metinler.
