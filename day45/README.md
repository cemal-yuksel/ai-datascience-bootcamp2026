# Gün 45 — Spor Salonu Yoğunluk Tahmini

Day44’ün görsel ve pedagojik düzeniyle hazırlanmış, uçtan uca bir makine öğrenmesi projesi. Random Forest teorisi tekrar edilmez; veri, model geliştirme ve değerlendirme öne çıkar.

## Çalıştırma

Python 3.12 ile doğrulanmıştır. Bu klasörü çalışma dizini seçin, `pip install -r requirements.txt` ile bağımlılıkları kurun ve `day45.ipynb` dosyasında **Restart Kernel and Run All** çalıştırın. `day45.html` kaydedilmiş çıktıların tarayıcı önizlemesidir; SVG görseller için `assets/` klasörü yanında kalmalıdır.

## Proje akışı

1. İş problemi, tahmin anı ve kaynak planlama senaryosu
2. Kurulum, sürümler ve ortak görsel tema
3. Veri sözlüğü ve kaynak kimliği
4. Eksik, tekrar, hedef ve zaman bütünlüğü denetimleri
5. Gözlenen günlerle eğitim / doğrulama / kilitli final test ayrımı
6. Eğitim verisinde saat, gün ve yoğunluk keşfi
7. Sıcaklık, tatil, dönem ve korelasyon incelemesi
8. Sızıntısız imputer / scaler / model pipeline’ı
9. MAE, RMSE, R² ve iki baseline
10. Referanstaki altı algoritmanın karşılaştırılması
11. KNN / Random Forest araması ve ileri zaman CV’si
12. Kilitli final test, gerçek–tahmin ve tolerans analizi
13. Artıklar, segmentler ve dönem kayması
14. Permütasyon ve RF MDI önemi
15. YBS karar senaryosu, referans rastgele bölme deneyi ve model teslimi
16. Çalıştırılmış yönetici özeti, kontrol listesi, quiz ve geliştirme görevleri

## Dosyalar

- `day45.ipynb`: Ana ders ve proje notebook’u; çalıştırılmış çıktılar içerir.
- `day45.html`: Notebook’un HTML önizlemesi.
- `15-gym_crowdedness.csv`: Özgün veri; değiştirilmemiştir.
- `15-RandomForestRegressor.ipynb`: Özgün uygulama referansı; değiştirilmemiştir.
- `assets/`: Day44’ten uyarlanmış SVG kapak, bölüm banner’ları ve kutu etiketleri.
- `outputs/figures/`: Kaydedilen grafikler.
- `outputs/reports/`: Kalite, metrik, arama, tahmin ve karar CSV’leri.
- `outputs/models/`: Pipeline paketi, model kartı ve sürüm bilgileri.

## Değerlendirme sınırları

Ana test, son %25 gözlenen takvim günüdür. Geliştirme içindeki aramalar gün bazında 3 ileri zaman katı ve 1 gözlenen gün boşluk kullanır. Sonraki rastgele bölme ayrı bir tanısal deneydir ve final model seçimini etkilemez. Referanstaki 100 arama yerine RF’de 12 kombinasyon, KNN’de 6 aday denenir. Sıcaklık birimi kaynakta doğrulanmadığından özgün ölçek korunur. Canlı kullanımda sıcaklık tahmininin hatası ayrıca değerlendirilmelidir. 50 kişi eşiği, 10 kişi toleransı ve 3:1 maliyet oranı gerçek salon politikası değil, eğitim senaryosudur.

## Kaynaklar

Veri ve uygulama: bu klasördeki özgün CSV / notebook. Görsel ve anlatım şablonu: `../day44/day44.ipynb`.

- [Kaggle veri bağlantısı](https://www.kaggle.com/datasets/nsrose7224/crowdedness-at-the-campus-gym/data)
- [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
