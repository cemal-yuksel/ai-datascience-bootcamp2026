# Proje Notları (Claude için)

## Commit mesajı stili

Her gün (Day NN) için commit başlığı şu kalıpta yazılır:

```text
<gün konusuna uygun emoji> Day NN · <konunun özünü anlatan, akılda kalan başlık>
```

Örnekler:

- 🌳 Day 43 · Veriden kurala, kuraldan karara: Karar Ağaçları
- 🌲 Day 44 · Tek ağaç değil, bir orman: Topluluk Öğrenmesi ve Random Forest
- 🏋️ Day 45 · Dürüst skor, görkemli vitrin

Kurallar:

- `docs(dayNN):`, `feat:`, `Day45:` gibi teknik önek **kullanılmaz**.
- Emoji, günün konusunu yansıtır (ağaç → 🌳, orman → 🌲, spor salonu → 🏋️).
- Başlık, proje senaryosunu veya ana dersi anlatır; "güncelle", "düzelt" gibi sönük fiillerle bitmez.
- Gövde, kısa bir özet ve maddelenmiş içerikten oluşur (yeni görseller, bölümler, sonuçlar).
- Bir gün için tek, derli toplu commit tercih edilir; küçük düzeltmeler ana commit'e birleştirilir.
- Her commit mesajı ortamın istediği `Co-Authored-By` ve `Claude-Session` satırlarıyla biter.

## Kullanıcı PDF veya Jupyter notebook gönderdiğinde

Kullanıcı bir `.pdf` ya da `.ipynb` eklediğinde (genellikle `/root/.claude/uploads/...` altında) aşağıdaki
akış her seferinde yeniden anlatılmadan uygulanır.

### Ortak kurallar

- Dosya **referanstır**: önce tamamını oku (notebook için hücre hücre kaynak kod + markdown; PDF için
  `pages` ile sayfa sayfa). Okumadan işe başlama.
- Referanstan **içerik kopyalanmaz**; yalnızca izlediği yol (veri hazırlama → keşif → bölme → kodlama →
  model → ayar → metrik sırası, ele aldığı konular, kullandığı yöntemler) öğrenilir. Cümleler, kod ve
  veri seti birebir alınmaz; özgün anlatım ve kod yazılır.
- Dosyaya ait veri seti repoda yoksa ve ağdan alınamıyorsa kullanıcıya bildir; uydurma veriyi gerçekmiş
  gibi sunma. Yerine erişilebilir, gerçek bir veri seti seç ve nedenini notebook'ta açıkla.
- Yüklenen dosyayı repoya kopyalama (kullanıcı özellikle istemedikçe).

### Notebook (`.ipynb`) geldiğinde

- İstenen dosya adıyla (ör. `day47.ipynb`) `dayNN/` klasöründe **yeni** bir notebook oluştur.
- Biçim, yapı ve kalite **Day 44 ile aynı** olmalı: hero/yol haritası/bölüm SVG'leri (`assets/`),
  etiket görselleri, animasyonlu diyagramlar ve GIF'ler, `outputs/figures` ve `outputs/reports`,
  `README.md`, `requirements.txt`, veri seti dosyası (`NN-ad.csv`).
- Uçtan uca makine öğrenmesi projesi yaz: senaryo → veri kalitesi → EDA → sızıntısız pipeline →
  model karşılaştırması → ayar → hata/adalet/iş analizi → sonuç. Notebook çıktıları (hücre outputs)
  çalıştırılmış ve kayıtlı olmalı.
- Konu başlığı dar olsa bile kullanıcı kaç algoritma istediyse (ör. "en az 18") o kadarını dene ve
  karşılaştır.

### PDF geldiğinde

- PDF ders notu/makale/kaynak olarak ele alınır: içeriği özetle ya da istenen çıktıya (notebook, README,
  ders notu) dönüştür; Day 44 biçimini ve kuralları uygula.
- Bilimsel içerik varsa kullanıcı tercihleri geçerlidir: güncel literatür taraması, dolaylı atıf
  (`(B, APA 7, A'dan aktarma)`) ve yanıt sonunda APA 7 `KAYNAKÇA`. Salt kod/betik isteklerinde bu biçim
  kullanılmaz.

### İş bitince

- Kök `README.md`'yi aşağıdaki "Her yeni gün eklendiğinde" bölümüne göre güncelle.
- Tek, derli toplu commit at (yukarıdaki commit stili) ve istenen dal üzerine `git push -u origin <dal>` ile
  pushla. Kullanıcı istemedikçe PR açma.

## Kök README.md: her yeni gün eklendiğinde

Bootcamp ≈ 70 günde bitecek (kurs adı "100 Günlük Kamp" olsa da repo kendi hızında ilerler). Kök
`README.md`, repodaki **gerçek** durumu yansıtan vitrindir. Her yeni gün (Day NN) eklendiğinde, o günün
commit'ine dahil olacak şekilde README aşağıdaki gibi güncellenir; kullanıcının ayrıca istemesi beklenmez.

Stil: mevcut görkemli düzen korunur (typing SVG, shields rozetleri, icons8 ikonlu HTML tabloları, `yaml`
kod blokları, `<details>` modülleri, emoji başlıklar). Yeni bölüm uydurulmaz, var olanlar doldurulur.

Güncellenecek yerler (README'de `<!-- ILERLEME:... -->` işaretleri var):

1. **`ILERLEME:ROZET`**: İlerleme rozeti `NN/70 gün (%X)` ve "Son Gün" rozeti (`Day NN · Konu`).
2. **Typing SVG**: `NN Gün Tamamlandı · Hedef 70 Gün` satırı (URL kodlu).
3. **`ILERLEME:SAYILAR`**: tamamlanan gün, notebook, veri seti, algoritma yarışı ve GIF/grafik/SVG sayıları.
   Sayılar elle tahmin edilmez, ölçülür:
   - notebook: `find . -name "*.ipynb" -not -path "./.git/*" | wc -l`
   - veri: `find . \( -name "*.csv" -o -name "*.xlsx" -o -name "*.db" \) -not -path "./.git/*" -not -path "*/outputs/*" -not -path "*/processed/*" -not -path "*/reports/*" | wc -l`
     (Day 57 itibarıyla 35 dosya; aynı verinin kopyaları (Kapıdağ D24/D25) ve türetilmiş dosyalar
     (D37 işlenmiş, D43 `aday_araclar.csv`) düşülünce README'deki **32**. Yeni gün genelde +1 ekler.)
   - görsel: `find . -name "*.gif" | wc -l`, `*.png`, `*.svg` aynı şekilde.
   - algoritma yarışı: 12+ algoritmanın aynı bölmede karşılaştırıldığı gün sayısı (+1 gerekiyorsa).
4. **`ILERLEME:CUBUK`**: 20 karelik çubuk (`round(NN/70*20)` dolu kare), yüzde, son durak ve sıradaki gün.
5. **Öğrenme Yolculuğu** ve **Zorluk Seviyesi**: ilgili modülün gün aralığı/sayısı ve durumu (`✅` / `🔜`).
   Yeni bir konu ailesi başlarsa "Son Etap" kartından modül ayrılır; gün aralıkları 70'e tamamlanır.
6. **Gün Gün Müfredat**: günün satırı ilgili modül tablosuna eklenir (Day 58+ için `YENI-GUN-BURAYA`
   işaretinin altındaki Modül 13 tablosu; "🔜 Yakında" satırı kalan gün aralığına göre daraltılır).
   Başlık sütunu, günün **commit başlığının aynısıdır** (`<emoji> **Day NN · başlık**`), link `dayNN/`.
7. **Proje Vitrini**: senaryo, yarışın büyüklüğü, öne çıkan sonuç ve dürüst ders. Sayılar yalnızca o günün
   README'sinden / çalıştırılmış hücre çıktılarından alınır; uydurulmaz, yuvarlama günün README'siyle aynı.
8. **Veri Setleri**: yeni veri seti uygun sektör kartına `• Ad (DNN)` olarak eklenir; başlıktaki toplam güncellenir.
9. **Teknolojiler**: yalnızca notebook'ta gerçekten `import` edilen yeni bir kütüphane rozet olarak eklenir.
10. İsteğe bağlı: günün en etkileyici GIF'i **Animasyon Galerisi**ne eklenebilir (galeri 6–8 GIF'i geçmesin;
    gerekirse en eskisi çıkarılır).

Kurallar:

- Bağlantılar göreli olmalı (`day57/`, `day10%2611/...`); var olmayan dosyaya link verilmez.
- Doğrulanamayan pazarlama iddiası (öğrenci sayısı, "Fortune 500", Discord/YouTube linki vb.) eklenmez.
- Day 70 tamamlandığında rozetler `70/70 (%100)`, "Son Etap" kartı `✅` ve kupa bölümü "tamamlandı" olur.
