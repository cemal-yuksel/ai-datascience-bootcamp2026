"""Day 50 · Kaliforniya konut projesi — pipeline içinde kullanılan özellik mühendisliği.

Bu sınıf notebook dışında, ayrı bir dosyada durur: `joblib` ile kaydedilen model,
başka bir süreçte yüklenirken sınıfı bu dosyadan bulabilsin diye.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Ham sütunlar (hedef ve etiket hariç)
SAYISAL = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
           "population", "households", "median_income"]
KATEGORIK = ["ocean_proximity"]
HAM_GIRDI = SAYISAL + KATEGORIK

# Kaliforniya'nın büyük şehir merkezleri (enlem, boylam) — "şehre uzaklık" özelliği için
SEHIRLER = {
    "San Francisco": (37.77, -122.42),
    "Los Angeles": (34.05, -118.24),
    "San Diego": (32.72, -117.16),
    "San Jose": (37.34, -121.89),
    "Sacramento": (38.58, -121.49),
}


def uzaklik_km(enlem, boylam, sehir_enlem, sehir_boylam):
    """İki nokta arası yaklaşık mesafe (km): haversine formülü."""
    r = 6371.0
    f1, f2 = np.radians(enlem), np.radians(sehir_enlem)
    df = f2 - f1
    dl = np.radians(sehir_boylam - boylam)
    a = np.sin(df / 2) ** 2 + np.cos(f1) * np.cos(f2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


class KonutOzellikleri(BaseEstimator, TransformerMixin):
    """Ham tablodan oranlar ve şehir uzaklıkları üretir (satır bazlı: eğitimden hiçbir şey öğrenmez, sızıntı yok).

    mod = "ham"      → yalnızca ham sütunlar (karşılaştırma için)
    mod = "oran"     → ham + oran özellikleri (oda/hane, yatak/oda, kişi/hane)
    mod = "tam"      → ham + oranlar + şehir uzaklıkları (varsayılan)
    """

    def __init__(self, mod="tam"):
        self.mod = mod

    def fit(self, X, y=None):
        self.feature_names_in_ = np.array(pd.DataFrame(X).columns, dtype=object)
        return self

    def get_feature_names_out(self, input_features=None):
        """Çıktı sütun adları (ColumnTransformer ve özellik önemi grafikleri için)."""
        ad = list(self.feature_names_in_ if input_features is None else input_features)
        if self.mod in ("oran", "tam"):
            ad += ["oda_hane", "yatak_oda_orani", "kisi_hane"]
        if self.mod == "tam":
            ad += ["en_yakin_sehir_km"]
        return np.array(ad, dtype=object)

    def transform(self, X):
        d = pd.DataFrame(X).copy()
        if self.mod in ("oran", "tam"):
            d["oda_hane"] = d["total_rooms"] / d["households"]
            d["yatak_oda_orani"] = d["total_bedrooms"] / d["total_rooms"]
            d["kisi_hane"] = d["population"] / d["households"]
        if self.mod == "tam":
            kolonlar = []
            for ad, (en, bo) in SEHIRLER.items():
                k = "km_" + ad.split()[-1].lower()
                d[k] = uzaklik_km(d["latitude"], d["longitude"], en, bo)
                kolonlar.append(k)
            d["en_yakin_sehir_km"] = d[kolonlar].min(axis=1)
            d = d.drop(columns=kolonlar)               # tek sütun yeter: en yakın şehre uzaklık
        return d

    def set_output(self, *, transform=None):           # pandas çıktısı isteyen ColumnTransformer ile uyum
        return self


def isaretli_log(a):
    """İşaretli log dönüşümü: sağa çarpık sayım sütunlarını (oda, nüfus …) yumuşatır; pickle için modül düzeyinde tanımlı."""
    return np.sign(a) * np.log1p(np.abs(a))
