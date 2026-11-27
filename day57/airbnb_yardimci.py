"""
Gün 57 · Yoğunluk tabanlı kümeleme — New York Airbnb yardımcı modülü
====================================================================

Bu dosya iki notebook tarafından da kullanılır. Kaydedilen modelin başka bir
Python sürecinde yüklenebilmesi için elle yazılmış kümeleyiciler burada durur.

İçerik
------
- veri_oku()             : Kaggle "New York City Airbnb Open Data" dosyasını okur, Türkçe sütun adları verir
- KmProjeksiyon          : enlem/boylamı (derece) şehrin ortasına göre kilometre ızgarasına çevirir
- nyc_haritasi()         : ilçe sınırlarını (nyc_ilce_sinirlari.json) matplotlib eksenine çizer
- dbcv_skoru()           : yoğunluk tabanlı küme geçerliliği (DBCV, Moulavi ve ark., 2014)
- kume_ozeti()           : küme sayısı, gürültü oranı, en büyük kümenin payı
- OrnekleYay             : O(n²) bellek isteyen algoritmaları örneklemde kurup 1-NN ile tüm veriye yayar
- YogunlukTepeleri       : "Density Peaks" (Rodriguez & Laio, 2014)
- IzgaraYogunlugu        : ızgara tabanlı yoğunluk kümelemesi (yoğun hücrelerin bağlı bileşenleri)
- PaylasilanKomsu        : paylaşılan en yakın komşu (SNN / Jarvis–Patrick) kümelemesi
- KMedoids               : merkez yerine gerçek bir ilanı "temsilci" seçen K-Medoids
- RastgeleTaban          : hiçbir şey öğrenmeyen karşılaştırma tabanı
- YogunlukAtayici        : predict() yöntemi olmayan DBSCAN / HDBSCAN'e "yeni ilanı odağa ata" yeteneği verir
- ozgun_hdbscan()        : scikit-learn HDBSCAN ayarını özgün `hdbscan` kütüphanesine (approximate_predict) taşır
- odak_ata()             : kaydedilmiş modeli yükleyip ham ilan kayıtlarına odak atar
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, minimum_spanning_tree
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator, ClusterMixin, TransformerMixin, clone
from sklearn.neighbors import NearestNeighbors

KLASOR = Path(__file__).resolve().parent
VERI_YOLU = KLASOR / "28-nyc-airbnb.csv"
HARITA_YOLU = KLASOR / "nyc_ilce_sinirlari.json"
MODEL_YOLU = KLASOR / "outputs" / "model" / "airbnb_odak_model.joblib"

# ── Sütun adları (Kaggle veri sözlüğüne göre) ───────────────────────────────
SUTUN_TR = {
    "id": "İlan no",
    "host_id": "Ev sahibi no",
    "neighbourhood_group": "İlçe",
    "neighbourhood": "Mahalle",
    "latitude": "Enlem",
    "longitude": "Boylam",
    "room_type": "Oda tipi",
    "price": "Fiyat",
    "minimum_nights": "En az gece",
    "number_of_reviews": "Yorum sayısı",
    "last_review": "Son yorum",
    "reviews_per_month": "Aylık yorum",
    "calculated_host_listings_count": "Ev sahibinin ilan sayısı",
    "availability_365": "Yıllık müsaitlik",
}
ODA_TR = {"Entire home/apt": "Tüm ev", "Private room": "Özel oda", "Shared room": "Paylaşımlı oda"}
ILCE_SIRA = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
ILCE_RENK = {"Manhattan": "#E5A100", "Brooklyn": "#2B6CB0", "Queens": "#D1495B",
             "Bronx": "#2E9E6B", "Staten Island": "#6C5CE7"}
KONUM = ["Enlem", "Boylam"]

# Kilometre dönüşümü için sabitler (WGS-84 elipsoidinde 40,7° enlem civarı)
KM_ENLEM = 110.574          # 1 derece enlem ≈ 110,574 km
KM_BOYLAM_EKVATOR = 111.320  # ekvatorda 1 derece boylam ≈ 111,320 km (cos(enlem) ile küçülür)


def veri_oku(yol: str | Path = VERI_YOLU) -> pd.DataFrame:
    """Ham Kaggle dosyasını okur; sütunları Türkçeleştirir, oda tipini Türkçe yazar."""
    df = pd.read_csv(yol).rename(columns=SUTUN_TR)
    df["Oda tipi"] = df["Oda tipi"].map(ODA_TR).fillna(df["Oda tipi"])
    return df


# ── 1) Derece → kilometre ───────────────────────────────────────────────────
class KmProjeksiyon(BaseEstimator, TransformerMixin):
    """Enlem/boylamı şehrin ortasını (0, 0) alan bir kilometre ızgarasına çevirir.

    Şehir ölçeğinde (≈ 50 km) eşdikdörtgen (equirectangular) yaklaşım metre düzeyinde
    doğrudur. Merkez **yalnızca eğitim verisinden** öğrenilir (fit), böylece test ilanları
    dönüşüme bilgi sızdırmaz. Çıktı: [x_km (doğu), y_km (kuzey)].
    """

    def __init__(self, enlem_sutun: str = "Enlem", boylam_sutun: str = "Boylam"):
        self.enlem_sutun = enlem_sutun
        self.boylam_sutun = boylam_sutun

    def _ayir(self, X):
        if isinstance(X, pd.DataFrame):
            return X[self.enlem_sutun].to_numpy(float), X[self.boylam_sutun].to_numpy(float)
        X = np.asarray(X, float)
        return X[:, 0], X[:, 1]

    def fit(self, X, y=None):
        enlem, boylam = self._ayir(X)
        self.enlem0_, self.boylam0_ = float(np.mean(enlem)), float(np.mean(boylam))
        self.km_boylam_ = KM_BOYLAM_EKVATOR * np.cos(np.radians(self.enlem0_))
        return self

    def transform(self, X):
        enlem, boylam = self._ayir(X)
        return np.c_[(boylam - self.boylam0_) * self.km_boylam_, (enlem - self.enlem0_) * KM_ENLEM]

    def ters(self, Z):
        """km → (enlem, boylam)."""
        Z = np.asarray(Z, float)
        return np.c_[Z[:, 1] / KM_ENLEM + self.enlem0_, Z[:, 0] / self.km_boylam_ + self.boylam0_]

    def get_feature_names_out(self, input_features=None):
        return np.array(["x_km", "y_km"])


# ── 2) Harita ───────────────────────────────────────────────────────────────
def _ilce_sinirlari(yol: str | Path = HARITA_YOLU):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)["features"]


def nyc_haritasi(ax, proj: KmProjeksiyon | None = None, dolgu="#F3F4F6", kenar="#9CA3AF", lw=0.7,
                 ilce_renk: dict | None = None, alpha=1.0, yazi=False, z=0):
    """İlçe sınırlarını çizer. proj verilirse km ızgarasında, verilmezse derece cinsinden çizer."""
    from matplotlib.patches import Polygon
    for f in _ilce_sinirlari():
        ad = f["properties"]["ilce"]
        renk = (ilce_renk or {}).get(ad, dolgu)
        en_buyuk, alan_max = None, -1
        for poligon in f["geometry"]["coordinates"]:
            dis = np.asarray(poligon[0])                           # [boylam, enlem]
            P = proj.transform(np.c_[dis[:, 1], dis[:, 0]]) if proj is not None else dis
            ax.add_patch(Polygon(P, closed=True, facecolor=renk, edgecolor=kenar, lw=lw, alpha=alpha, zorder=z))
            alan = np.ptp(P[:, 0]) * np.ptp(P[:, 1])
            if alan > alan_max:
                alan_max, en_buyuk = alan, P
        if yazi and en_buyuk is not None:
            ax.text(*en_buyuk.mean(0), ad, ha="center", va="center", fontsize=9, color="#374151",
                    fontweight="bold", alpha=.75, zorder=z + 5)
    ax.set_aspect("equal")
    return ax


# ── 3) Kalite ölçütleri ─────────────────────────────────────────────────────
def kume_ozeti(et) -> dict:
    """Küme sayısı (gürültü hariç), gürültü oranı ve en büyük kümenin tüm veriye oranı."""
    et = np.asarray(et)
    kume = et[et >= 0]
    n_kume = len(np.unique(kume))
    return {"Odak sayısı": n_kume,
            "Gürültü %": 100 * float(np.mean(et < 0)),
            "En büyük odak %": 100 * (np.bincount(kume).max() / len(et) if n_kume else 0.0)}


def _tum_nokta_cekirdek(D: np.ndarray, boyut: int) -> np.ndarray:
    """DBCV'nin 'tüm noktalar çekirdek mesafesi': komşuların ters mesafelerinin ortalamasından türetilir."""
    with np.errstate(divide="ignore"):
        T = np.where(D > 0, (1.0 / np.where(D > 0, D, 1.0)) ** boyut, 0.0)
    ort = T.sum(1) / max(len(D) - 1, 1)
    with np.errstate(divide="ignore"):
        return np.where(ort > 0, ort ** (-1.0 / boyut), 0.0)


def dbcv_skoru(X, et, en_az: int = 3, ayrintili: bool = False):
    """Density-Based Clustering Validation (Moulavi ve ark., 2014).

    -1 ile +1 arasında; yüksek değer = kümeler içte yoğun ve birbirinden seyrek bir
    'boşlukla' ayrılmış. Gürültü noktaları paydaya girer ama kümelere katkı vermez.
    `en_az` noktadan küçük kümeler (genelde örneklemde kalan kırıntılar) gürültü sayılır.
    """
    X = np.asarray(X, float)
    et = np.asarray(et).copy()
    boyut = X.shape[1]
    for k in np.unique(et[et >= 0]):
        if np.sum(et == k) < en_az:
            et[et == k] = -1
    kumeler = np.unique(et[et >= 0])
    if len(kumeler) < 2:
        return (np.nan, {}) if ayrintili else np.nan
    ic_dugum, cekirdek, seyreklik = {}, {}, {}
    for k in kumeler:
        P = X[et == k]
        D = cdist(P, P)
        c = _tum_nokta_cekirdek(D, boyut)
        MR = np.maximum(D, np.maximum.outer(c, c))
        np.fill_diagonal(MR, 0)
        mst = minimum_spanning_tree(csr_matrix(MR + 1e-12 * (MR == 0) * (1 - np.eye(len(P))))).tocoo()
        derece = np.bincount(np.r_[mst.row, mst.col], minlength=len(P))
        ic = np.where(derece > 1)[0]
        if len(ic) == 0:                       # 2–3 noktalı kümede iç düğüm olmayabilir
            ic = np.arange(len(P))
        ic_kume = np.isin(mst.row, ic) & np.isin(mst.col, ic)
        seyreklik[k] = mst.data[ic_kume].max() if ic_kume.any() else mst.data.max()
        ic_dugum[k], cekirdek[k] = P[ic], c[ic]
    ayrisma = {k: np.inf for k in kumeler}
    for i, a in enumerate(kumeler):
        for b in kumeler[i + 1:]:
            D = cdist(ic_dugum[a], ic_dugum[b])
            m = np.maximum(D, np.maximum.outer(cekirdek[a], cekirdek[b])).min()
            ayrisma[a] = min(ayrisma[a], m)
            ayrisma[b] = min(ayrisma[b], m)
    gecerlilik = {k: (ayrisma[k] - seyreklik[k]) / max(ayrisma[k], seyreklik[k]) for k in kumeler}
    toplam = sum(np.sum(et == k) * v for k, v in gecerlilik.items()) / len(et)
    return (float(toplam), gecerlilik) if ayrintili else float(toplam)


# ── 4) Ölçeklenemeyen algoritmalar için "örneklemde kur, komşuyla yay" ───────
class OrnekleYay(BaseEstimator, ClusterMixin):
    """Spektral, Affinity Propagation, bağlantılı hiyerarşik gibi O(n²) bellek isteyen
    algoritmaları `n_ornek` ilanlık rastgele örneklemde kurar; diğer tüm ilanlara en yakın
    örneklem ilanının etiketini (gürültü dahil) verir."""

    def __init__(self, tahminci=None, n_ornek: int = 4000, random_state: int = 42):
        self.tahminci = tahminci
        self.n_ornek = n_ornek
        self.random_state = random_state

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        rng = np.random.default_rng(self.random_state)
        idx = rng.choice(len(X), min(self.n_ornek, len(X)), replace=False)
        self.model_ = clone(self.tahminci)
        self.ornek_ = X[idx]
        self.ornek_et_ = np.asarray(self.model_.fit_predict(self.ornek_))
        self.nn_ = NearestNeighbors(n_neighbors=1).fit(self.ornek_)
        self.labels_ = self.predict(X)
        return self

    def predict(self, X):
        return self.ornek_et_[self.nn_.kneighbors(np.asarray(X, float))[1][:, 0]]


# ── 5) Elle yazılmış yoğunluk algoritmaları ─────────────────────────────────
class YogunlukTepeleri(BaseEstimator, ClusterMixin):
    """Density Peaks (Rodriguez & Laio, 2014).

    1) Her ilanın yoğunluğu ρ: `dc` km yarıçapındaki komşu sayısı.
    2) δ: kendisinden daha yoğun en yakın ilana uzaklık.
    3) Hem ρ hem δ büyük olan `n_kume` ilan "tepe" (merkez) seçilir.
    4) Diğer ilanlar, yoğunluk azalan sırayla, 'kendinden yoğun en yakın komşusunun' kümesine katılır.
    5) ρ < `gurultu_rho` olan ilanlar gürültü (-1) sayılır.
    """

    def __init__(self, n_kume: int = 30, dc: float = 0.25, gurultu_rho: int = 0, k_aday: int = 60):
        self.n_kume = n_kume
        self.dc = dc
        self.gurultu_rho = gurultu_rho
        self.k_aday = k_aday

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        n = len(X)
        nn = NearestNeighbors().fit(X)
        rho = np.array([len(a) for a in nn.radius_neighbors(X, self.dc, return_distance=False)], float)
        rho = rho + np.random.default_rng(0).uniform(0, 1e-3, n)          # eşitlikleri boz
        uz, ind = nn.kneighbors(X, n_neighbors=min(self.k_aday, n))
        delta, ust = np.full(n, np.inf), np.full(n, -1)
        for i in range(n):
            daha_yogun = rho[ind[i]] > rho[i]
            if daha_yogun.any():
                j = np.argmax(daha_yogun)                               # komşular mesafe sırasında
                delta[i], ust[i] = uz[i, j], ind[i, j]
        kalan = np.where(ust < 0)[0]                                     # yakın komşularda daha yoğunu yok
        for i in kalan:
            aday = np.where(rho > rho[i])[0]
            if len(aday):
                d = np.linalg.norm(X[aday] - X[i], axis=1)
                delta[i], ust[i] = d.min(), aday[d.argmin()]
        delta[np.isinf(delta)] = np.nanmax(delta[np.isfinite(delta)]) if np.isfinite(delta).any() else 1.0
        gamma = rho * delta
        merkez = np.argsort(-gamma)[: self.n_kume]
        et = np.full(n, -1)
        et[merkez] = np.arange(len(merkez))
        for i in np.argsort(-rho):
            if et[i] < 0:
                et[i] = et[ust[i]] if ust[i] >= 0 else 0
        et[rho < self.gurultu_rho] = -1
        self.rho_, self.delta_, self.merkez_ = rho, delta, merkez
        self.labels_ = et
        return self


class IzgaraYogunlugu(BaseEstimator, ClusterMixin):
    """Şehri `hucre` km'lik karelere böler; içinde en az `esik` ilan olan hücreler 'yoğun'dur.
    Birbirine değen (8 yönlü) yoğun hücreler aynı odağı oluşturur; seyrek hücrelerdeki ilanlar gürültüdür."""

    def __init__(self, hucre: float = 0.25, esik: int = 20):
        self.hucre = hucre
        self.esik = esik

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        self.koken_ = X.min(0)
        ij = np.floor((X - self.koken_) / self.hucre).astype(int)
        boyut = ij.max(0) + 1
        sayim = np.zeros(boyut, int)
        np.add.at(sayim, (ij[:, 0], ij[:, 1]), 1)
        etiket, n = ndimage.label(sayim >= self.esik, structure=np.ones((3, 3)))
        et = etiket[ij[:, 0], ij[:, 1]] - 1
        self.sayim_, self.izgara_ = sayim, etiket
        self.labels_ = et
        return self


class PaylasilanKomsu(BaseEstimator, ClusterMixin):
    """Jarvis–Patrick / SNN kümelemesi: iki ilan, birbirinin `k` en yakın komşusu arasındaysa VE
    en az `ortak` komşuyu paylaşıyorsa bağlanır. Bağlı bileşenler küme olur; `en_az`'dan küçükler gürültüdür.
    Yoğunluk farkına dayanıklıdır, çünkü mesafeye değil 'ortak tanıdık' sayısına bakar (Ertöz ve ark., 2003)."""

    def __init__(self, k: int = 20, ortak: int = 10, en_az: int = 30):
        self.k = k
        self.ortak = ortak
        self.en_az = en_az

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        n = len(X)
        ind = NearestNeighbors(n_neighbors=self.k + 1).fit(X).kneighbors(X, return_distance=False)[:, 1:]
        A = csr_matrix((np.ones(n * self.k), (np.repeat(np.arange(n), self.k), ind.ravel())), shape=(n, n))
        karsilikli = A.multiply(A.T)                              # yalnızca karşılıklı komşular
        ortak_sayi = (A @ A.T).multiply(karsilikli)               # paylaşılan komşu sayısı
        guclu = (ortak_sayi >= self.ortak).astype(int)
        _, et = connected_components(guclu, directed=False)
        boy = np.bincount(et)
        kucuk = boy[et] < self.en_az
        et = np.where(kucuk, -1, et)
        _, et_yeni = np.unique(et[et >= 0], return_inverse=True)
        sonuc = np.full(n, -1)
        sonuc[et >= 0] = et_yeni
        self.labels_ = sonuc
        return self


class KMedoids(BaseEstimator, ClusterMixin):
    """K-Medoids (Voronoi yinelemesi): her kümenin temsilcisi gerçek bir ilandır.
    Başlangıç k-means++ ile seçilir; tam veri yerine OrnekleYay içinde kullanılması önerilir."""

    def __init__(self, n_clusters: int = 8, max_iter: int = 50, random_state: int = 42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        rng = np.random.default_rng(self.random_state)
        merkez = [rng.integers(len(X))]
        d2 = np.sum((X - X[merkez[0]]) ** 2, 1)
        for _ in range(1, self.n_clusters):
            merkez.append(rng.choice(len(X), p=d2 / d2.sum()))
            d2 = np.minimum(d2, np.sum((X - X[merkez[-1]]) ** 2, 1))
        merkez = np.array(merkez)
        for _ in range(self.max_iter):
            et = cdist(X, X[merkez]).argmin(1)
            yeni = merkez.copy()
            for k in range(self.n_clusters):
                uye = np.where(et == k)[0]
                if len(uye):
                    yeni[k] = uye[cdist(X[uye], X[uye]).sum(1).argmin()]
            if np.array_equal(yeni, merkez):
                break
            merkez = yeni
        self.medoid_idx_, self.cluster_centers_ = merkez, X[merkez]
        self.labels_ = cdist(X, X[merkez]).argmin(1)
        return self

    def predict(self, X):
        return cdist(np.asarray(X, float), self.cluster_centers_).argmin(1)


class RastgeleTaban(BaseEstimator, ClusterMixin):
    """Her ilana rastgele bir odak numarası verir. 'Hiçbir şey öğrenmeyen' alt sınır."""

    def __init__(self, n_clusters: int = 8, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def fit(self, X, y=None):
        self.labels_ = np.random.default_rng(self.random_state).integers(0, self.n_clusters, len(X))
        return self


# ── 6) DBSCAN / HDBSCAN'e predict() kazandırmak ─────────────────────────────
def ozgun_hdbscan(model):
    """scikit-learn HDBSCAN ayarlarını, yeni nokta tahmini (approximate_predict) sunan özgün
    `hdbscan` kütüphanesine (McInnes ve ark., 2017) taşır. Diğer modelleri olduğu gibi döndürür."""
    from sklearn.cluster import HDBSCAN as SkHDBSCAN
    if not isinstance(model, SkHDBSCAN):
        return model
    import hdbscan
    p = model.get_params()
    return hdbscan.HDBSCAN(min_cluster_size=p["min_cluster_size"], min_samples=p["min_samples"],
                           cluster_selection_method=p["cluster_selection_method"],
                           cluster_selection_epsilon=p["cluster_selection_epsilon"],
                           max_cluster_size=p["max_cluster_size"] or 0, prediction_data=True)


class YogunlukAtayici(BaseEstimator, ClusterMixin):
    """Yoğunluk tabanlı kümeleyiciyi eğitir ve yeni ilanları eğitimde bulunan odaklara atar.
    Yeni ilan eğitimi DEĞİŞTİRMEZ (odaklar sabit kalır; test bilgisi modele sızmaz).

    - Özgün `hdbscan` modeli (prediction_data=True): HDBSCAN'in kendi `approximate_predict` yöntemi.
      Yeni nokta, eğitimdeki yoğunluk ağacında hangi kümenin 'yaşadığı' seviyeye düşüyorsa oraya katılır.
    - DBSCAN: 'çekirdek komşuluğu' kuralı. En yakın çekirdek ilan eps içindeyse onun odağı, değilse -1
      (DBSCAN'in sınır noktalarına uyguladığı kuralın aynısı).
    - Diğerleri: en yakın gürültü olmayan eğitim ilanının kendi `min_samples` yarıçapı içindeyse onun odağı.

    transform(X) → üyelik gücü (0–1): HDBSCAN'de approximate_predict'in verdiği güç, diğerlerinde
    max(0, 1 − uzaklık / yarıçap).
    """

    def __init__(self, kumeleyici=None, min_samples: int | None = None):
        self.kumeleyici = kumeleyici
        self.min_samples = min_samples

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        self.model_ = clone(self.kumeleyici).fit(X)
        et = np.asarray(self.model_.labels_)
        self.hdbscan_ = hasattr(self.model_, "prediction_data_")
        if hasattr(self.model_, "core_sample_indices_"):           # DBSCAN
            cekirdek = np.asarray(self.model_.core_sample_indices_)
            yaricap = np.full(len(cekirdek), float(self.model_.eps))
        else:
            ms = self.min_samples or getattr(self.model_, "min_samples", None) \
                or getattr(self.model_, "min_cluster_size", 5)
            cekirdek = np.where(et >= 0)[0]
            yaricap = NearestNeighbors(n_neighbors=int(ms)).fit(X).kneighbors(X[cekirdek])[0][:, -1]
        self.cekirdek_X_, self.cekirdek_et_, self.yaricap_ = X[cekirdek], et[cekirdek], yaricap
        self.nn_ = NearestNeighbors(n_neighbors=1).fit(self.cekirdek_X_)
        self.labels_ = et
        return self

    def _ata(self, X):
        X = np.asarray(X, float)
        if self.hdbscan_:
            import hdbscan
            et, guc = hdbscan.approximate_predict(self.model_, X)
            return np.asarray(et), np.asarray(guc)
        uz, ind = self.nn_.kneighbors(X)
        uz, ind = uz[:, 0], ind[:, 0]
        icinde = uz <= self.yaricap_[ind]
        return np.where(icinde, self.cekirdek_et_[ind], -1), np.clip(1 - uz / np.maximum(self.yaricap_[ind], 1e-9), 0, 1)

    def predict(self, X):
        return self._ata(X)[0]

    def transform(self, X):
        return self._ata(X)[1][:, None]


def odak_ata(kayit, model_yolu: str | Path = MODEL_YOLU, meta_yolu: str | Path | None = None) -> pd.DataFrame:
    """Kaydedilmiş boru hattını yükler; 'Enlem' ve 'Boylam' sütunlu ham kayıtlara odak atar."""
    import joblib
    model = joblib.load(model_yolu)
    meta_yolu = Path(meta_yolu) if meta_yolu else Path(model_yolu).with_name("meta.json")
    meta = json.loads(Path(meta_yolu).read_text(encoding="utf-8"))
    df = pd.DataFrame(kayit).copy()
    et = model.predict(df[KONUM])
    oran = model.transform(df[KONUM])[:, 0]
    adlar = {int(k): v for k, v in meta["odak_adlari"].items()}
    df["Odak"] = et
    df["Odak adı"] = [adlar.get(int(e), "Dağınık (odak dışı)") for e in et]
    df["Üyelik gücü"] = oran.round(2)
    return df
