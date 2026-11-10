"""Day 51 · Boston mahalle projesi — pipeline içinde kullanılan yardımcılar.

Bu dosya notebook dışında durur: `joblib` ile kaydedilen model başka bir süreçte
yüklenirken sınıfı buradan bulabilsin diye (Day 49 ve Day 50'deki düzenle aynı).
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# CSV'de başlık satırı yok; sütun adları veri setinin özgün tanımından (Harrison ve Rubinfeld, 1978) alınır.
SUTUNLAR = ["CRIM", "ZN", "INDUS", "CHAS", "NOX", "RM", "AGE", "DIS", "RAD", "TAX", "PTRATIO", "B", "LSTAT", "MEDV"]

# Türkçe okunur açıklamalar (grafiklerde ve raporlarda kullanılır)
ACIKLAMA = {
    "CRIM": "Kişi başı suç oranı", "ZN": "Büyük parsel (25 bin ft² üstü) konut payı %", "INDUS": "Sanayi (perakende dışı) arazi payı %",
    "CHAS": "Charles Nehri kıyısı (1/0)", "NOX": "Azot oksit derişimi (hava kirliliği)", "RM": "Konut başına ortalama oda sayısı",
    "AGE": "1940 öncesi yapılmış konut payı %", "DIS": "Beş iş merkezine ağırlıklı uzaklık", "RAD": "Çevre yoluna erişim endeksi",
    "TAX": "Emlak vergisi (10 bin $ başına)", "PTRATIO": "Öğrenci/öğretmen oranı", "B": "Irksal bileşenli endeks (KULLANILMAZ)",
    "LSTAT": "Düşük statülü nüfus payı %", "MEDV": "Konut medyan değeri (bin $, 1970'ler)",
}

ESIK_BIN_DOLAR = 25.0          # "premium mahalle" tanımı: medyan değer ≥ 25 bin $
SINIF_ADLARI = ["Standart", "Premium"]

# Modelde kullanılacak ham sütunlar (MEDV hedefin kendisi, B etik gerekçeyle dışarıda)
OZELLIK_A = ["CRIM", "ZN", "INDUS", "CHAS", "NOX", "RM", "AGE", "DIS", "RAD", "TAX", "PTRATIO", "LSTAT"]
OZELLIK_B = [s for s in OZELLIK_A if s != "LSTAT"]      # senaryo B: nüfusun statüsünü ölçen sütun olmadan
ILCE_SUTUNLARI = ["INDUS", "RAD", "TAX", "PTRATIO", "ZN"]  # aynı kasabadaki mahallelerde ortak çıkan sütunlar


def veri_oku(yol):
    """Başlıksız, boşlukla ayrılmış CSV'yi okur ve sütunlara ad verir."""
    return pd.read_csv(yol, sep=r"\s+", header=None, names=SUTUNLAR)


def ilce_kimligi(df):
    """Kasaba (ilçe) kimliği veride yok. Kasabaya özgü sütunları (vergi, sanayi, okul...) aynı olan mahalleleri
    aynı gruba koyarak bir *vekil* kimlik üretir. Amaç: komşu mahalle sızıntısını ölçmek (grup bazlı doğrulama)."""
    return df.groupby(ILCE_SUTUNLARI).ngroup().to_numpy()


class BostonOzellikleri(BaseEstimator, TransformerMixin):
    """Ham tablodan alan bilgisine dayalı oranlar üretir (satır bazlı: eğitimden hiçbir şey öğrenmez → sızıntı yok).

    mod = "ham"   → yalnızca verilen sütunlar
    mod = "oran"  → ham + oranlar (oda/statü, vergi/oda, kirlilik×sanayi, uzaklık/erişim)
    """

    def __init__(self, mod="oran"):
        self.mod = mod

    def fit(self, X, y=None):
        self.feature_names_in_ = np.array(pd.DataFrame(X).columns, dtype=object)
        return self

    def get_feature_names_out(self, input_features=None):
        ad = list(self.feature_names_in_ if input_features is None else input_features)
        if self.mod == "oran":
            ad += [a for a in ("oda_statu", "vergi_oda", "kirlilik_sanayi", "uzaklik_erisim") if self._gerekli(a, ad)]
        return np.array(ad, dtype=object)

    @staticmethod
    def _gerekli(oran, mevcut):
        need = {"oda_statu": {"RM", "LSTAT"}, "vergi_oda": {"TAX", "RM"}, "kirlilik_sanayi": {"NOX", "INDUS"},
                "uzaklik_erisim": {"DIS", "RAD"}}[oran]
        return need.issubset(set(mevcut))

    def transform(self, X):
        d = pd.DataFrame(X).copy()
        if self.mod == "oran":
            if {"RM", "LSTAT"}.issubset(d.columns):
                d["oda_statu"] = d["RM"] / d["LSTAT"]                 # çok oda + düşük statü payı → premium işareti
            if {"TAX", "RM"}.issubset(d.columns):
                d["vergi_oda"] = d["TAX"] / d["RM"]                   # oda başına vergi yükü
            if {"NOX", "INDUS"}.issubset(d.columns):
                d["kirlilik_sanayi"] = d["NOX"] * d["INDUS"]          # sanayi + kirlilik birlikte
            if {"DIS", "RAD"}.issubset(d.columns):
                d["uzaklik_erisim"] = d["DIS"] / d["RAD"]             # merkeze uzaklık / yol erişimi
        return d

    def set_output(self, *, transform=None):                           # pandas çıktısı isteyen yapılarla uyum
        return self
