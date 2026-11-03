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
