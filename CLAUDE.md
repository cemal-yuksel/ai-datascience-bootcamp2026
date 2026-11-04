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

- Tek, derli toplu commit at (yukarıdaki commit stili) ve istenen dal üzerine `git push -u origin <dal>` ile
  pushla. Kullanıcı istemedikçe PR açma.
