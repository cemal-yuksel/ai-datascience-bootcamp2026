"""Gün 55 yardımcıları: veri okuma, özellik üretimi, Türkçe adlar ve elle yazılmış kümeleyiciler.

Kümeleyici sınıflar (K-Medoids, K-Medyan, Bulanık C-Ortalamalar, rastgele taban) bu dosyada durur;
böylece `joblib` ile kaydedilen boru hatları başka bir süreçte de sorunsuz yüklenir.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.validation import check_array, check_is_fitted

VERI_YOLU = Path(__file__).parent / "26-customer-personality.csv"
VERI_SON_TARIH = pd.Timestamp("2014-07-01")      # verideki en son kayıt tarihinden sonraki ilk gün

# Ürün ve kanal sütunları (orijinal Kaggle adlarıyla)
URUNLER = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
URUN_TR = {"MntWines": "Şarap", "MntFruits": "Meyve", "MntMeatProducts": "Et", "MntFishProducts": "Balık",
           "MntSweetProducts": "Tatlı", "MntGoldProds": "Altın"}
KANALLAR = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
KAMPANYALAR = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]

# Kümelemede kullanılan 7 çekirdek özellik (davranış + temel ekonomik durum)
KUME_OZELLIKLERI = ["Gelir", "Yaş", "Çocuk", "Toplam harcama", "Alışveriş sayısı", "İndirim oranı", "Web ziyaret/ay"]
LOG_SUTUNLARI = ["Gelir", "Toplam harcama", "Alışveriş sayısı"]   # sağa çarpık; log1p ile sıkıştırılır

MEDENI_TR = {"Married": "Evli", "Together": "Birlikte", "Single": "Bekâr", "Divorced": "Boşanmış",
             "Widow": "Dul", "Alone": "Bekâr", "Absurd": "Belirsiz", "YOLO": "Belirsiz"}
EGITIM_TR = {"Basic": "Temel", "2n Cycle": "Ön lisans", "Graduation": "Lisans", "Master": "Yüksek lisans", "PhD": "Doktora"}


def veri_oku(yol=None):
    """Ham veriyi (2.240 satır, 29 sütun) olduğu gibi okur."""
    return pd.read_csv(yol or VERI_YOLU, encoding="utf-8-sig")


def ozellik_uret(ham):
    """Ham tablodan satır bazlı (veriden öğrenilmeyen, sızıntısız) özellikler üretir.

    Hiçbir istatistik (ortalama, medyan…) burada hesaplanmaz; bu yüzden bölmeden önce
    çağrılması güvenlidir. Eksik gelir NaN olarak kalır ve boru hattındaki doldurucuya bırakılır.
    """
    d = ham.copy()
    harcama = d[URUNLER].sum(axis=1)
    alisveris = d[KANALLAR].sum(axis=1)
    toplam_islem = (alisveris + d["NumDealsPurchases"]).replace(0, np.nan)
    f = pd.DataFrame(index=d.index)
    f["Gelir"] = d["Income"]
    f["Yaş"] = 2014 - d["Year_Birth"]                        # veri 2014'te toplandı; bugüne göre değil
    f["Çocuk"] = d["Kidhome"] + d["Teenhome"]
    f["Toplam harcama"] = harcama
    f["Alışveriş sayısı"] = alisveris
    f["İndirim oranı"] = (d["NumDealsPurchases"] / toplam_islem).fillna(0.0)
    f["Web ziyaret/ay"] = d["NumWebVisitsMonth"]
    # Profil için ek bilgiler (kümelemede kullanılmaz)
    f["Küçük çocuk"] = d["Kidhome"]
    f["Ergen"] = d["Teenhome"]
    f["Kıdem (gün)"] = (VERI_SON_TARIH - pd.to_datetime(d["Dt_Customer"])).dt.days
    f["Son alışverişten beri (gün)"] = d["Recency"]
    for u in URUNLER:
        f[f"{URUN_TR[u]} payı"] = (d[u] / harcama.replace(0, np.nan)).fillna(0.0)
    for k, ad in zip(KANALLAR, ["Web", "Katalog", "Mağaza"]):
        f[f"{ad} payı"] = (d[k] / alisveris.replace(0, np.nan)).fillna(0.0)
    f["Önceki kampanya kabulü"] = d[KAMPANYALAR].sum(axis=1)
    f["Şikâyet"] = d["Complain"]
    f["Eğitim"] = d["Education"].map(EGITIM_TR)
    f["Medeni durum"] = d["Marital_Status"].map(MEDENI_TR)
    f["Son kampanya yanıtı"] = d["Response"]
    return f


def log1p_donustur(X):
    """Negatif olmayan sütunları log(1+x) ile sıkıştırır (FunctionTransformer için adlandırılmış fonksiyon)."""
    return np.log1p(np.asarray(X, dtype=float))


# ─────────────────────────── Elle yazılmış kümeleyiciler ───────────────────────────

def _kpp_tohum(X, k, rng, metrik="oklid"):
    """k-means++ tarzı tohumlama: her yeni merkez, mevcut merkezlere uzak noktalardan olasılıkla seçilir."""
    n = X.shape[0]
    merkez = [X[rng.integers(n)]]
    for _ in range(1, k):
        C = np.array(merkez)
        if metrik == "manhattan":
            d = np.abs(X[:, None, :] - C[None, :, :]).sum(-1).min(1)
        else:
            d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1).min(1)
        p = d / d.sum() if d.sum() > 0 else np.full(n, 1 / n)
        merkez.append(X[rng.choice(n, p=p)])
    return np.array(merkez)


class KMedyan(BaseEstimator, ClusterMixin):
    """K-Medyan: Manhattan uzaklığı + her kümenin **medyanı** merkez olur (aykırı değere daha dayanıklı)."""

    def __init__(self, n_clusters=3, n_init=10, max_iter=100, random_state=None):
        self.n_clusters, self.n_init, self.max_iter, self.random_state = n_clusters, n_init, max_iter, random_state

    def _ata(self, X, C):
        return np.abs(X[:, None, :] - C[None, :, :]).sum(-1)

    def fit(self, X, y=None):
        X = check_array(X, dtype=float); rng = np.random.default_rng(self.random_state)
        en_iyi = (np.inf, None, None)
        for _ in range(self.n_init):
            C = _kpp_tohum(X, self.n_clusters, rng, "manhattan")
            for _ in range(self.max_iter):
                lab = self._ata(X, C).argmin(1)
                yeni = np.array([np.median(X[lab == j], 0) if (lab == j).any() else C[j] for j in range(self.n_clusters)])
                if np.allclose(yeni, C): break
                C = yeni
            D = self._ata(X, C); lab = D.argmin(1); maliyet = D.min(1).sum()
            if maliyet < en_iyi[0]: en_iyi = (maliyet, C, lab)
        self.inertia_, self.cluster_centers_, self.labels_ = en_iyi
        return self

    def predict(self, X):
        check_is_fitted(self, "cluster_centers_")
        return self._ata(check_array(X, dtype=float), self.cluster_centers_).argmin(1)

    def transform(self, X):
        """Her müşterinin her merkeze Manhattan uzaklığı."""
        check_is_fitted(self, "cluster_centers_")
        return self._ata(check_array(X, dtype=float), self.cluster_centers_)


class KMedoids(BaseEstimator, ClusterMixin):
    """K-Medoids (dönüşümlü sürüm): merkez, kümenin **gerçek bir üyesidir** (ortalama değil)."""

    def __init__(self, n_clusters=3, n_init=5, max_iter=100, random_state=None):
        self.n_clusters, self.n_init, self.max_iter, self.random_state = n_clusters, n_init, max_iter, random_state

    def fit(self, X, y=None):
        X = check_array(X, dtype=float); rng = np.random.default_rng(self.random_state)
        D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))       # n×n uzaklık (küçük veri için uygun)
        en_iyi = (np.inf, None)
        for _ in range(self.n_init):
            C = _kpp_tohum(X, self.n_clusters, rng)
            med = np.array([np.argmin(((X - c) ** 2).sum(1)) for c in C])
            for _ in range(self.max_iter):
                lab = D[:, med].argmin(1)
                yeni = med.copy()
                for j in range(self.n_clusters):
                    uye = np.where(lab == j)[0]
                    if len(uye): yeni[j] = uye[D[np.ix_(uye, uye)].sum(1).argmin()]
                if np.array_equal(yeni, med): break
                med = yeni
            maliyet = D[:, med].min(1).sum()
            if maliyet < en_iyi[0]: en_iyi = (maliyet, med)
        self.inertia_, self.medoid_indices_ = en_iyi
        self.cluster_centers_ = X[self.medoid_indices_]
        self.labels_ = self.predict(X)
        return self

    def predict(self, X):
        return self.transform(X).argmin(1)

    def transform(self, X):
        """Her müşterinin her medoide Öklid uzaklığı."""
        check_is_fitted(self, "cluster_centers_")
        X = check_array(X, dtype=float)
        return np.sqrt(((X[:, None, :] - self.cluster_centers_[None, :, :]) ** 2).sum(-1))


class BulanikCOrtalama(BaseEstimator, ClusterMixin):
    """Bulanık C-Ortalamalar (Fuzzy C-Means): her müşteri her kümeye **bir üyelik derecesiyle** aittir."""

    def __init__(self, n_clusters=3, m=2.0, max_iter=300, tol=1e-6, random_state=None):
        self.n_clusters, self.m, self.max_iter, self.tol, self.random_state = n_clusters, m, max_iter, tol, random_state

    def _uyelik(self, X, C):
        d = np.sqrt(((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)) + 1e-12
        us = 2.0 / (self.m - 1.0)
        return 1.0 / ((d[:, :, None] / d[:, None, :]) ** us).sum(-1)

    def fit(self, X, y=None):
        X = check_array(X, dtype=float); rng = np.random.default_rng(self.random_state)
        C = _kpp_tohum(X, self.n_clusters, rng)
        for _ in range(self.max_iter):
            U = self._uyelik(X, C); W = U ** self.m
            yeni = (W.T @ X) / W.sum(0)[:, None]
            if np.abs(yeni - C).max() < self.tol: C = yeni; break
            C = yeni
        self.cluster_centers_ = C; self.membership_ = self._uyelik(X, C); self.labels_ = self.membership_.argmax(1)
        return self

    def predict(self, X):
        check_is_fitted(self, "cluster_centers_")
        return self._uyelik(check_array(X, dtype=float), self.cluster_centers_).argmax(1)

    def transform(self, X):
        """Her müşterinin her merkeze Öklid uzaklığı (üyelik değil)."""
        check_is_fitted(self, "cluster_centers_")
        X = check_array(X, dtype=float)
        return np.sqrt(((X[:, None, :] - self.cluster_centers_[None, :, :]) ** 2).sum(-1))


class RastgeleTaban(BaseEstimator, ClusterMixin):
    """Taban çizgisi: müşterileri **rastgele** k gruba atar. Hiçbir algoritma bunun altında kalmamalı."""

    def __init__(self, n_clusters=3, random_state=None):
        self.n_clusters, self.random_state = n_clusters, random_state

    def fit(self, X, y=None):
        X = check_array(X, dtype=float)
        self.labels_ = np.random.default_rng(self.random_state).integers(0, self.n_clusters, X.shape[0])
        self.cluster_centers_ = np.array([X[self.labels_ == j].mean(0) for j in range(self.n_clusters)])
        return self


# ─────────────────────────── İşletmede kullanım ───────────────────────────

def segment_ata(musteri, model=None, meta=None):
    """Tek müşteri (ham sütunlu sözlük) ya da ham tablo alır; segment adını ve merkeze uzaklığını döndürür."""
    import joblib, json
    klasor = Path(__file__).parent / "outputs" / "model"
    model = model or joblib.load(klasor / "musteri_segment_model.joblib")
    meta = meta or json.loads((klasor / "meta.json").read_text(encoding="utf-8"))
    ham = pd.DataFrame([musteri]) if isinstance(musteri, dict) else pd.DataFrame(musteri)
    X = ozellik_uret(ham)[meta["ozellikler"]]
    kume = model.predict(X)
    uzak = model.transform(X).min(axis=1) if hasattr(model, "transform") else np.full(len(X), np.nan)
    adlar = meta["segment_adlari"]
    return pd.DataFrame({"Segment no": kume, "Segment": [adlar[str(int(k))] for k in kume],
                         "Merkeze uzaklık": np.round(uzak, 3),
                         "Sıra dışı mı?": uzak > meta["aykiri_esik"]})
