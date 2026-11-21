"""
Gün 56 · Hiyerarşik kümeleme — ülke verisi yardımcı modülü
==========================================================

Bu dosya iki notebook tarafından da kullanılır ve kaydedilen modelin başka bir
Python sürecinde yüklenebilmesi için elle yazılmış kümeleyicileri barındırır.

İçerik
------
- veri_oku()            : Kaggle "Unsupervised Learning on Country Data" dosyasını okur,
                          sütunlara Türkçe ad verir, Türkçe ülke adı + kıta + EAGÜ bilgisini ekler
- isaretli_log()        : negatif değer alabilen sütunlar (enflasyon) için işaretli log
- dunya_haritasi()      : Natural Earth sınırlarıyla (dunya_sinirlari.json) matplotlib haritası
- DIANA                 : bölerek (yukarıdan aşağı) hiyerarşik kümeleme (Kaufman & Rousseeuw)
- ScipyBaglanti         : SciPy'nin scikit-learn'de olmayan bağlantıları (weighted, centroid, median)
- KMedoids              : merkez yerine gerçek bir ülkeyi "temsilci" seçen K-Medoids
- RastgeleTaban         : hiçbir şey öğrenmeyen karşılaştırma tabanı
- AgacAtayici           : predict() yöntemi olmayan kümeleyicilere (ör. AgglomerativeClustering)
                          "yeni gelen ülkeyi en yakın küme merkezine ata" yeteneği kazandırır
- ihtiyac_ata()         : kaydedilmiş modeli yükleyip ham ülke kayıtlarına segment atar
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.base import BaseEstimator, ClusterMixin, clone

KLASOR = Path(__file__).resolve().parent
VERI_YOLU = KLASOR / "27-country-data.csv"
HARITA_YOLU = KLASOR / "dunya_sinirlari.json"
MODEL_YOLU = KLASOR / "outputs" / "model" / "ulke_segment_model.joblib"

# ── Sütun adları (Kaggle veri sözlüğüne göre) ───────────────────────────────
SUTUN_TR = {
    "child_mort": "Çocuk ölümü",        # 5 yaş altı ölüm, 1000 canlı doğumda
    "exports": "İhracat",               # kişi başı GSYH'nin %'si olarak mal-hizmet ihracatı
    "health": "Sağlık harcaması",       # kişi başı GSYH'nin %'si olarak toplam sağlık harcaması
    "imports": "İthalat",               # kişi başı GSYH'nin %'si olarak mal-hizmet ithalatı
    "income": "Gelir",                  # kişi başı net gelir
    "inflation": "Enflasyon",           # toplam GSYH'nin yıllık büyüme hızı ile ölçülen enflasyon (%)
    "life_expec": "Yaşam beklentisi",   # yeni doğan bir bebeğin beklenen yaşam süresi (yıl)
    "total_fer": "Doğurganlık",         # kadın başına çocuk sayısı
    "gdpp": "Kişi başı GSYH",           # kişi başı gayrisafi yurt içi hasıla
}
OZELLIKLER = list(SUTUN_TR.values())
BIRIM = {"Çocuk ölümü": "‰ (1000 doğumda)", "İhracat": "% GSYH", "Sağlık harcaması": "% GSYH", "İthalat": "% GSYH",
         "Gelir": "$ / kişi", "Enflasyon": "%", "Yaşam beklentisi": "yıl", "Doğurganlık": "çocuk / kadın",
         "Kişi başı GSYH": "$ / kişi"}
# Sağa çarpık, yalnızca pozitif değer alan sütunlar → log(1+x)
LOG_SUTUNLARI = ["Çocuk ölümü", "İhracat", "İthalat", "Gelir", "Kişi başı GSYH", "Doğurganlık"]
# Negatif değer alabilen çarpık sütun → işaretli log: sign(x)·log(1+|x|)
ISARETLI_LOG_SUTUNLARI = ["Enflasyon"]

# ── Ülke adları (Türkçe), kıta (Natural Earth sınıflaması) ──────────────────
ULKE_BILGI = {
    "Afghanistan": ("Afganistan", "Asya"), "Albania": ("Arnavutluk", "Avrupa"), "Algeria": ("Cezayir", "Afrika"),
    "Angola": ("Angola", "Afrika"), "Antigua and Barbuda": ("Antigua ve Barbuda", "Kuzey Amerika"),
    "Argentina": ("Arjantin", "Güney Amerika"), "Armenia": ("Ermenistan", "Asya"), "Australia": ("Avustralya", "Okyanusya"),
    "Austria": ("Avusturya", "Avrupa"), "Azerbaijan": ("Azerbaycan", "Asya"), "Bahamas": ("Bahamalar", "Kuzey Amerika"),
    "Bahrain": ("Bahreyn", "Asya"), "Bangladesh": ("Bangladeş", "Asya"), "Barbados": ("Barbados", "Kuzey Amerika"),
    "Belarus": ("Belarus", "Avrupa"), "Belgium": ("Belçika", "Avrupa"), "Belize": ("Belize", "Kuzey Amerika"),
    "Benin": ("Benin", "Afrika"), "Bhutan": ("Butan", "Asya"), "Bolivia": ("Bolivya", "Güney Amerika"),
    "Bosnia and Herzegovina": ("Bosna-Hersek", "Avrupa"), "Botswana": ("Botsvana", "Afrika"),
    "Brazil": ("Brezilya", "Güney Amerika"), "Brunei": ("Brunei", "Asya"), "Bulgaria": ("Bulgaristan", "Avrupa"),
    "Burkina Faso": ("Burkina Faso", "Afrika"), "Burundi": ("Burundi", "Afrika"), "Cambodia": ("Kamboçya", "Asya"),
    "Cameroon": ("Kamerun", "Afrika"), "Canada": ("Kanada", "Kuzey Amerika"), "Cape Verde": ("Yeşil Burun Adaları", "Afrika"),
    "Central African Republic": ("Orta Afrika Cumhuriyeti", "Afrika"), "Chad": ("Çad", "Afrika"),
    "Chile": ("Şili", "Güney Amerika"), "China": ("Çin", "Asya"), "Colombia": ("Kolombiya", "Güney Amerika"),
    "Comoros": ("Komorlar", "Afrika"), "Congo, Dem. Rep.": ("Kongo Demokratik Cumhuriyeti", "Afrika"),
    "Congo, Rep.": ("Kongo Cumhuriyeti", "Afrika"), "Costa Rica": ("Kosta Rika", "Kuzey Amerika"),
    "Cote d'Ivoire": ("Fildişi Sahili", "Afrika"), "Croatia": ("Hırvatistan", "Avrupa"), "Cyprus": ("Kıbrıs", "Asya"),
    "Czech Republic": ("Çekya", "Avrupa"), "Denmark": ("Danimarka", "Avrupa"),
    "Dominican Republic": ("Dominik Cumhuriyeti", "Kuzey Amerika"), "Ecuador": ("Ekvador", "Güney Amerika"),
    "Egypt": ("Mısır", "Afrika"), "El Salvador": ("El Salvador", "Kuzey Amerika"),
    "Equatorial Guinea": ("Ekvator Ginesi", "Afrika"), "Eritrea": ("Eritre", "Afrika"), "Estonia": ("Estonya", "Avrupa"),
    "Fiji": ("Fiji", "Okyanusya"), "Finland": ("Finlandiya", "Avrupa"), "France": ("Fransa", "Avrupa"),
    "Gabon": ("Gabon", "Afrika"), "Gambia": ("Gambiya", "Afrika"), "Georgia": ("Gürcistan", "Asya"),
    "Germany": ("Almanya", "Avrupa"), "Ghana": ("Gana", "Afrika"), "Greece": ("Yunanistan", "Avrupa"),
    "Grenada": ("Grenada", "Kuzey Amerika"), "Guatemala": ("Guatemala", "Kuzey Amerika"), "Guinea": ("Gine", "Afrika"),
    "Guinea-Bissau": ("Gine-Bissau", "Afrika"), "Guyana": ("Guyana", "Güney Amerika"), "Haiti": ("Haiti", "Kuzey Amerika"),
    "Hungary": ("Macaristan", "Avrupa"), "Iceland": ("İzlanda", "Avrupa"), "India": ("Hindistan", "Asya"),
    "Indonesia": ("Endonezya", "Asya"), "Iran": ("İran", "Asya"), "Iraq": ("Irak", "Asya"), "Ireland": ("İrlanda", "Avrupa"),
    "Israel": ("İsrail", "Asya"), "Italy": ("İtalya", "Avrupa"), "Jamaica": ("Jamaika", "Kuzey Amerika"),
    "Japan": ("Japonya", "Asya"), "Jordan": ("Ürdün", "Asya"), "Kazakhstan": ("Kazakistan", "Asya"),
    "Kenya": ("Kenya", "Afrika"), "Kiribati": ("Kiribati", "Okyanusya"), "Kuwait": ("Kuveyt", "Asya"),
    "Kyrgyz Republic": ("Kırgızistan", "Asya"), "Lao": ("Laos", "Asya"), "Latvia": ("Letonya", "Avrupa"),
    "Lebanon": ("Lübnan", "Asya"), "Lesotho": ("Lesotho", "Afrika"), "Liberia": ("Liberya", "Afrika"),
    "Libya": ("Libya", "Afrika"), "Lithuania": ("Litvanya", "Avrupa"), "Luxembourg": ("Lüksemburg", "Avrupa"),
    "Macedonia, FYR": ("Kuzey Makedonya", "Avrupa"), "Madagascar": ("Madagaskar", "Afrika"), "Malawi": ("Malavi", "Afrika"),
    "Malaysia": ("Malezya", "Asya"), "Maldives": ("Maldivler", "Asya"), "Mali": ("Mali", "Afrika"), "Malta": ("Malta", "Avrupa"),
    "Mauritania": ("Moritanya", "Afrika"), "Mauritius": ("Mauritius", "Afrika"),
    "Micronesia, Fed. Sts.": ("Mikronezya", "Okyanusya"), "Moldova": ("Moldova", "Avrupa"), "Mongolia": ("Moğolistan", "Asya"),
    "Montenegro": ("Karadağ", "Avrupa"), "Morocco": ("Fas", "Afrika"), "Mozambique": ("Mozambik", "Afrika"),
    "Myanmar": ("Myanmar", "Asya"), "Namibia": ("Namibya", "Afrika"), "Nepal": ("Nepal", "Asya"),
    "Netherlands": ("Hollanda", "Avrupa"), "New Zealand": ("Yeni Zelanda", "Okyanusya"), "Niger": ("Nijer", "Afrika"),
    "Nigeria": ("Nijerya", "Afrika"), "Norway": ("Norveç", "Avrupa"), "Oman": ("Umman", "Asya"),
    "Pakistan": ("Pakistan", "Asya"), "Panama": ("Panama", "Kuzey Amerika"), "Paraguay": ("Paraguay", "Güney Amerika"),
    "Peru": ("Peru", "Güney Amerika"), "Philippines": ("Filipinler", "Asya"), "Poland": ("Polonya", "Avrupa"),
    "Portugal": ("Portekiz", "Avrupa"), "Qatar": ("Katar", "Asya"), "Romania": ("Romanya", "Avrupa"),
    "Russia": ("Rusya", "Avrupa"), "Rwanda": ("Ruanda", "Afrika"), "Samoa": ("Samoa", "Okyanusya"),
    "Saudi Arabia": ("Suudi Arabistan", "Asya"), "Senegal": ("Senegal", "Afrika"), "Serbia": ("Sırbistan", "Avrupa"),
    "Seychelles": ("Seyşeller", "Afrika"), "Sierra Leone": ("Sierra Leone", "Afrika"), "Singapore": ("Singapur", "Asya"),
    "Slovak Republic": ("Slovakya", "Avrupa"), "Slovenia": ("Slovenya", "Avrupa"),
    "Solomon Islands": ("Solomon Adaları", "Okyanusya"), "South Africa": ("Güney Afrika", "Afrika"),
    "South Korea": ("Güney Kore", "Asya"), "Spain": ("İspanya", "Avrupa"), "Sri Lanka": ("Sri Lanka", "Asya"),
    "St. Vincent and the Grenadines": ("Saint Vincent ve Grenadinler", "Kuzey Amerika"), "Sudan": ("Sudan", "Afrika"),
    "Suriname": ("Surinam", "Güney Amerika"), "Sweden": ("İsveç", "Avrupa"), "Switzerland": ("İsviçre", "Avrupa"),
    "Tajikistan": ("Tacikistan", "Asya"), "Tanzania": ("Tanzanya", "Afrika"), "Thailand": ("Tayland", "Asya"),
    "Timor-Leste": ("Doğu Timor", "Asya"), "Togo": ("Togo", "Afrika"), "Tonga": ("Tonga", "Okyanusya"),
    "Tunisia": ("Tunus", "Afrika"), "Turkey": ("Türkiye", "Asya"), "Turkmenistan": ("Türkmenistan", "Asya"),
    "Uganda": ("Uganda", "Afrika"), "Ukraine": ("Ukrayna", "Avrupa"), "United Arab Emirates": ("Birleşik Arap Emirlikleri", "Asya"),
    "United Kingdom": ("Birleşik Krallık", "Avrupa"), "United States": ("ABD", "Kuzey Amerika"),
    "Uruguay": ("Uruguay", "Güney Amerika"), "Uzbekistan": ("Özbekistan", "Asya"), "Vanuatu": ("Vanuatu", "Okyanusya"),
    "Venezuela": ("Venezuela", "Güney Amerika"), "Vietnam": ("Vietnam", "Asya"), "Yemen": ("Yemen", "Asya"),
    "Zambia": ("Zambiya", "Afrika"),
}

# BM En Az Gelişmiş Ülkeler (EAGÜ / LDC) listesi, 2018 itibarıyla 47 ülke (UN DESA / CDP).
# Listedeki Cibuti, Etiyopya, Somali, Güney Sudan, São Tomé ve Principe, Tuvalu bu veri setinde YOK.
# Bu bilgi kümelemede KULLANILMAZ; yalnızca dış doğrulama (bağımsız kanıt) içindir.
EAGU_2018 = {
    "Afghanistan", "Angola", "Bangladesh", "Benin", "Bhutan", "Burkina Faso", "Burundi", "Cambodia",
    "Central African Republic", "Chad", "Comoros", "Congo, Dem. Rep.", "Eritrea", "Gambia", "Guinea", "Guinea-Bissau",
    "Haiti", "Kiribati", "Lao", "Lesotho", "Liberia", "Madagascar", "Malawi", "Mali", "Mauritania", "Mozambique",
    "Myanmar", "Nepal", "Niger", "Rwanda", "Senegal", "Sierra Leone", "Solomon Islands", "Sudan", "Timor-Leste",
    "Togo", "Uganda", "Tanzania", "Vanuatu", "Yemen", "Zambia",
}

# Natural Earth'te adı farklı yazılan ülkeler
NE_AD = {"Bosnia and Herzegovina": "Bosnia and Herz.", "Central African Republic": "Central African Rep.",
         "Congo, Dem. Rep.": "Dem. Rep. Congo", "Congo, Rep.": "Congo", "Cote d'Ivoire": "Côte d'Ivoire",
         "Czech Republic": "Czechia", "Dominican Republic": "Dominican Rep.", "Equatorial Guinea": "Eq. Guinea",
         "Kyrgyz Republic": "Kyrgyzstan", "Lao": "Laos", "Macedonia, FYR": "North Macedonia",
         "Slovak Republic": "Slovakia", "Solomon Islands": "Solomon Is.", "United States": "United States of America"}
# Düşük çözünürlüklü haritada çokgeni olmayan küçük ada ülkeleri → yaklaşık konum (boylam, enlem), işaretçi ile çizilir
KUCUK_ULKE_KONUM = {"Antigua and Barbuda": (-61.8, 17.1), "Bahrain": (50.6, 26.1), "Barbados": (-59.6, 13.2),
                    "Cape Verde": (-23.6, 15.1), "Comoros": (43.3, -11.7), "Grenada": (-61.7, 12.1),
                    "Kiribati": (173.0, 1.4), "Maldives": (73.5, 4.2), "Malta": (14.4, 35.9), "Mauritius": (57.6, -20.3),
                    "Micronesia, Fed. Sts.": (158.2, 6.9), "Samoa": (-172.1, -13.8), "Seychelles": (55.5, -4.7),
                    "Singapore": (103.8, 1.35), "St. Vincent and the Grenadines": (-61.2, 13.25), "Tonga": (-175.2, -21.2)}


def veri_oku(yol: str | Path = VERI_YOLU) -> pd.DataFrame:
    """Ham CSV'yi okur; Türkçe sütun adları, Türkçe ülke adı, kıta ve EAGÜ bilgisini ekler."""
    ham = pd.read_csv(yol)
    d = ham.rename(columns=SUTUN_TR).rename(columns={"country": "Ülke (EN)"})
    d.insert(1, "Ülke", d["Ülke (EN)"].map(lambda u: ULKE_BILGI.get(u, (u, "?"))[0]))
    d["Kıta"] = d["Ülke (EN)"].map(lambda u: ULKE_BILGI.get(u, (u, "?"))[1])
    d["EAGÜ (BM 2018)"] = d["Ülke (EN)"].isin(EAGU_2018).astype(int)
    return d


def ticaret_kontrol(df: pd.DataFrame, esik: float = 1.0) -> pd.DataFrame:
    """İhracat ya da ithalatı GSYH'nin %1'inden az görünen kayıtları eksik (NaN) yapar.

    Dünyada dış ticareti ekonomisinin %1'inden küçük bir ülke yoktur; böyle bir değer büyük olasılıkla
    birim/veri giriş hatasıdır (bu veride: Myanmar, ihracat %0,109 · ithalat %0,066). Satır bazlı bir
    kuraldır, veriden istatistik öğrenmez; eksik değer daha sonra boru hattında EĞİTİM medyanıyla doldurulur.
    """
    d = df.copy()
    for s in ["İhracat", "İthalat"]:
        if s in d:
            d.loc[d[s] < esik, s] = np.nan
    return d


def isaretli_log(x):
    """sign(x)·log(1+|x|): sıfır çevresinde doğrusal, uçlarda logaritmik; negatif enflasyonu da sıkıştırır."""
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.log1p(np.abs(x))


def log1p_donustur(x):
    """FunctionTransformer için modül düzeyinde (joblib ile kaydedilebilir) log(1+x)."""
    return np.log1p(np.asarray(x, dtype=float))


# ── Harita ──────────────────────────────────────────────────────────────────
def dunya_haritasi(ax, renk: dict, varsayilan="#E5E7EB", kenar="#FFFFFF", kucuk_boy=46, baslik=None):
    """renk: {"Ülke (EN)": renk kodu}. Verideki ülkeler boyanır, diğerleri gri kalır."""
    from matplotlib.collections import PolyCollection
    sinir = json.loads(HARITA_YOLU.read_text(encoding="utf-8"))
    ters = {v: k for k, v in NE_AD.items()}
    poligon, boya = [], []
    for ne_ad, halkalar in sinir.items():
        r = renk.get(ters.get(ne_ad, ne_ad), varsayilan)
        for h in halkalar:
            poligon.append(np.asarray(h)); boya.append(r)
    ax.add_collection(PolyCollection(poligon, facecolors=boya, edgecolors=kenar, linewidths=.35))
    for u, (x, y) in KUCUK_ULKE_KONUM.items():
        if u in renk:
            ax.scatter(x, y, s=kucuk_boy, color=renk[u], edgecolor="#1F2937", linewidth=.6, zorder=5)
    ax.set_xlim(-180, 190); ax.set_ylim(-58, 84); ax.set_aspect("equal"); ax.axis("off")
    if baslik:
        ax.set_title(baslik)
    return ax


# ── Elle yazılmış kümeleyiciler ─────────────────────────────────────────────
class DIANA(BaseEstimator, ClusterMixin):
    """DIvisive ANAlysis: tek dev kümeden başlayıp her adımda çapı en büyük kümeyi ikiye böler.

    Bölme: kümede ortalama uzaklığı en büyük olan nokta "kıymık" grubu başlatır; sonra
    kalanlara kıymıktan daha yakın olan noktalar (fark > 0) tek tek kıymığa geçer.
    """

    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters

    def _bol(self, D, idx):
        alt = D[np.ix_(idx, idx)]
        n = len(idx)
        kiymik = [int(np.argmax(alt.sum(1) / max(n - 1, 1)))]
        kalan = [i for i in range(n) if i != kiymik[0]]
        while len(kalan) > 1:
            k_arr, s_arr = np.array(kalan), np.array(kiymik)
            ort_kalan = (alt[np.ix_(k_arr, k_arr)].sum(1)) / (len(kalan) - 1)
            ort_kiymik = alt[np.ix_(k_arr, s_arr)].mean(1)
            fark = ort_kalan - ort_kiymik
            if fark.max() <= 0:
                break
            j = kalan[int(np.argmax(fark))]
            kiymik.append(j); kalan.remove(j)
        return idx[np.array(kalan)], idx[np.array(kiymik)]

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        D = squareform(pdist(X))
        kumeler = [np.arange(len(X))]
        self.bolmeler_ = []                      # (bölünen küme boyu, çap) kayıtları — animasyon/teşhis için
        self.adimlar_ = [np.zeros(len(X), int)]  # her bölmeden sonraki etiketler
        while len(kumeler) < self.n_clusters:
            capl = [D[np.ix_(c, c)].max() if len(c) > 1 else -1 for c in kumeler]
            i = int(np.argmax(capl))
            if capl[i] <= 0:
                break
            a, b = self._bol(D, kumeler.pop(i))
            kumeler += [a, b]
            self.bolmeler_.append((len(a) + len(b), capl[i]))
            et = np.empty(len(X), int)
            for j, c in enumerate(kumeler):
                et[c] = j
            self.adimlar_.append(et)
        self.labels_ = self.adimlar_[-1]
        return self

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


class ScipyBaglanti(BaseEstimator, ClusterMixin):
    """SciPy linkage + fcluster(maxclust): weighted (WPGMA), centroid (UPGMC), median (WPGMC) vb."""

    def __init__(self, n_clusters=3, method="weighted"):
        self.n_clusters = n_clusters
        self.method = method

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.linkage_ = linkage(X, method=self.method, metric="euclidean")
        et = fcluster(self.linkage_, self.n_clusters, criterion="maxclust") - 1
        _, self.labels_ = np.unique(et, return_inverse=True)
        return self

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


class KMedoids(BaseEstimator, ClusterMixin):
    """Alternatifli K-Medoids: her kümenin temsilcisi, kümedeki toplam uzaklığı en küçük olan GERÇEK noktadır."""

    def __init__(self, n_clusters=3, n_init=10, max_iter=100, random_state=None):
        self.n_clusters, self.n_init, self.max_iter, self.random_state = n_clusters, n_init, max_iter, random_state

    def _bir_kez(self, X, D, rng):
        n = len(X)
        med = [int(rng.integers(n))]
        for _ in range(1, self.n_clusters):                     # k-medoids++ tohumlama
            d2 = D[:, med].min(1) ** 2
            med.append(int(rng.choice(n, p=d2 / d2.sum())))
        med = np.array(med)
        for _ in range(self.max_iter):
            et = D[:, med].argmin(1)
            yeni = med.copy()
            for j in range(self.n_clusters):
                uye = np.where(et == j)[0]
                if len(uye):
                    yeni[j] = uye[D[np.ix_(uye, uye)].sum(1).argmin()]
            if np.array_equal(yeni, med):
                break
            med = yeni
        et = D[:, med].argmin(1)
        return med, et, D[np.arange(n), med[et]].sum()

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        D = squareform(pdist(X))
        rng = np.random.default_rng(self.random_state)
        en_iyi = min((self._bir_kez(X, D, rng) for _ in range(self.n_init)), key=lambda t: t[2])
        self.medoid_indices_, self.labels_, self.inertia_ = en_iyi
        self.cluster_centers_ = X[self.medoid_indices_]
        return self

    def predict(self, X):
        return cdist(np.asarray(X, dtype=float), self.cluster_centers_).argmin(1)

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


class KonsensusHiyerarsik(BaseEstimator, ClusterMixin):
    """Konsensüs (birlikte-atanma) kümelemesi + hiyerarşik son adım (Monti ve ark., 2003 fikri).

    1) Verinin %oran'ı kadar alt örnek B kez çekilir; her birinde taban kümeleyici (Ward ya da K-Means) çalışır.
    2) Her ülke çifti için "birlikte örneklendiklerinde aynı kümeye düşme oranı" hesaplanır (konsensüs matrisi).
    3) 1 − konsensüs bir mesafe gibi kullanılarak ortalama/tam bağlantılı hiyerarşik kümeleme yapılır.
    Böylece tek bir ağacın tesadüflerine değil, yüzlerce ağacın ortak kararına dayanılır.
    """

    def __init__(self, n_clusters=3, B=30, oran=0.8, taban="ward", baglanti="average", random_state=None):
        self.n_clusters, self.B, self.oran, self.taban, self.baglanti, self.random_state = n_clusters, B, oran, taban, baglanti, random_state

    def fit(self, X, y=None):
        from sklearn.cluster import AgglomerativeClustering, KMeans
        X = np.asarray(X, dtype=float)
        n = len(X)
        rng = np.random.default_rng(self.random_state)
        ayni = np.zeros((n, n)); birlikte = np.zeros((n, n))
        for b in range(self.B):
            idx = np.sort(rng.choice(n, int(round(self.oran * n)), replace=False))
            if self.taban == "ward":
                et = AgglomerativeClustering(self.n_clusters).fit_predict(X[idx])
            else:
                et = KMeans(self.n_clusters, n_init=3, random_state=int(rng.integers(1_000_000))).fit_predict(X[idx])
            birlikte[np.ix_(idx, idx)] += 1
            ayni[np.ix_(idx, idx)] += (et[:, None] == et[None, :])
        self.konsensus_ = np.divide(ayni, birlikte, out=np.zeros_like(ayni), where=birlikte > 0)
        np.fill_diagonal(self.konsensus_, 1.0)
        self.labels_ = AgglomerativeClustering(self.n_clusters, metric="precomputed",
                                               linkage=self.baglanti).fit_predict(1 - self.konsensus_)
        return self

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


class RastgeleTaban(BaseEstimator, ClusterMixin):
    """Hiçbir şey öğrenmeyen taban: ülkelere rastgele etiket dağıtır. Gerçek algoritmalar bunu geçmeli."""

    def __init__(self, n_clusters=3, random_state=None):
        self.n_clusters, self.random_state = n_clusters, random_state

    def fit(self, X, y=None):
        self.labels_ = np.random.default_rng(self.random_state).integers(self.n_clusters, size=len(X))
        return self

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


class AgacAtayici(BaseEstimator, ClusterMixin):
    """predict() yöntemi olmayan bir kümeleyiciyi (ör. AgglomerativeClustering) sarar.

    fit(): kümeleyiciyi eğitim verisiyle kurar, her kümenin merkezini (ortalamasını) saklar.
    predict(): yeni gelen noktayı EN YAKIN KÜME MERKEZİNE atar (Ward bağlantısının mantığıyla uyumlu).
    transform(): her küme merkezine uzaklık (sıra dışı ülke tespiti için).
    """

    def __init__(self, kumeleyici=None):
        self.kumeleyici = kumeleyici

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.kumeleyici_ = clone(self.kumeleyici)
        self.labels_ = np.asarray(self.kumeleyici_.fit_predict(X))
        self.cluster_centers_ = np.array([X[self.labels_ == j].mean(0) for j in np.unique(self.labels_)])
        return self

    def predict(self, X):
        return cdist(np.asarray(X, dtype=float), self.cluster_centers_).argmin(1)

    def transform(self, X):
        return cdist(np.asarray(X, dtype=float), self.cluster_centers_)

    def fit_predict(self, X, y=None):
        return self.fit(X).labels_


# ── Kayıtlı modeli kullanma ─────────────────────────────────────────────────
def ihtiyac_ata(kayit, model_yolu: str | Path = MODEL_YOLU, meta_yolu: str | Path | None = None) -> pd.DataFrame:
    """Ham (Kaggle sütun adlı ya da Türkçe adlı) ülke kayıtlarına segment atar.

    kayit: tek bir dict ya da DataFrame. Dönen tabloda segment numarası, adı ve
    'sıra dışı' uyarısı (en yakın merkeze uzaklık eğitimdeki %99'luk dilimin üstündeyse) bulunur.
    """
    import joblib
    model_yolu = Path(model_yolu)
    meta = json.loads(Path(meta_yolu or model_yolu.with_name("meta.json")).read_text(encoding="utf-8"))
    model = joblib.load(model_yolu)
    df = pd.DataFrame([kayit]) if isinstance(kayit, dict) else pd.DataFrame(kayit).copy()
    df = ticaret_kontrol(df.rename(columns=SUTUN_TR))      # karar defterindeki kural: ticaret < %1 GSYH → eksik
    X = df[meta["ozellikler"]]
    seg = model.predict(X)
    uzak = model.transform(X).min(1)
    ad = {int(k): v for k, v in meta["segment_adlari"].items()}
    cikti = pd.DataFrame({"Ülke": df.get("country", df.get("Ülke (EN)", pd.Series(range(len(df))))).values,
                          "Segment": seg, "Segment adı": [ad[s] for s in seg],
                          "Merkeze uzaklık": np.round(uzak, 3), "Sıra dışı?": uzak > meta["aykiri_esik"]})
    return cikti
