"""Titanik projesi için veri okuma ve özellik üretimi (joblib ile kaydedilebilmesi için ayrı dosyada)."""
import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

VERI_YOLU = "22-titanic.csv"
UNVAN_ESLEME = {"Mr": "Mr", "Mrs": "Mrs", "Miss": "Miss", "Master": "Master", "Mme": "Mrs", "Ms": "Miss", "Mlle": "Miss"}
SAYISAL = ["Pclass", "Age", "SibSp", "Parch", "Fare", "AileBoyu", "YalnizMi", "BiletGrubu", "KisiBasiUcret", "YasEksik", "KabinVar"]
KATEGORIK = ["Sex", "Embarked", "Unvan", "Guverte"]


def veri_oku(yol=VERI_YOLU):
    """CSV'yi okur; ham sütunlara dokunmaz."""
    return pd.read_csv(yol)


def unvan_cikar(ad):
    """'Braund, Mr. Owen Harris' → 'Mr'. Nadir unvanlar 'Diger' olur."""
    m = re.search(r",\s*([^\.]+)\.", str(ad))
    u = m.group(1).strip() if m else "Diger"
    return UNVAN_ESLEME.get(u, "Diger")


def soyad_cikar(ad):
    return str(ad).split(",")[0].strip()


class OzellikUretici(BaseEstimator, TransformerMixin):
    """Ham Titanik tablosundan model özellikleri üretir.

    Önemli: Hedef (Survived) kullanılmaz. Bilet grubu boyutu tüm yolcu listesinden
    sayılır; bu, yolcu listesinin (hedef değil) bilgisidir ve tahmin anında da bilinir.
    """

    def __init__(self, bilet_sayilari=None):
        self.bilet_sayilari = bilet_sayilari

    def fit(self, X, y=None):
        self.bilet_sayilari_ = X["Ticket"].value_counts().to_dict() if self.bilet_sayilari is None else self.bilet_sayilari
        return self

    def transform(self, X):
        d = pd.DataFrame(index=X.index)
        d["Pclass"] = X["Pclass"].astype(float)
        d["Sex"] = X["Sex"].astype(str)
        d["Age"] = X["Age"].astype(float)
        d["SibSp"] = X["SibSp"].astype(float)
        d["Parch"] = X["Parch"].astype(float)
        d["Fare"] = X["Fare"].astype(float)
        d["Embarked"] = X["Embarked"].fillna("Bilinmiyor").astype(str)
        d["Unvan"] = X["Name"].map(unvan_cikar)
        d["AileBoyu"] = (X["SibSp"] + X["Parch"] + 1).astype(float)
        d["YalnizMi"] = (d["AileBoyu"] == 1).astype(float)
        d["BiletGrubu"] = X["Ticket"].map(lambda t: self.bilet_sayilari_.get(t, 1)).astype(float)
        d["KisiBasiUcret"] = d["Fare"] / d["BiletGrubu"].clip(lower=1)
        d["YasEksik"] = X["Age"].isna().astype(float)
        d["KabinVar"] = X["Cabin"].notna().astype(float)
        d["Guverte"] = X["Cabin"].fillna("Yok").astype(str).str[0]
        return d[SAYISAL + KATEGORIK]

    def get_feature_names_out(self, input_features=None):
        return np.array(SAYISAL + KATEGORIK)


class KategoriDonusturucu(BaseEstimator, TransformerMixin):
    """Kategorik sütunları pandas 'category' türüne çevirir (LightGBM'in doğal kategori desteği için).

    Eğitimde görülen kategoriler saklanır; tahmin anında yeni bir kategori gelirse NaN olur.
    """

    def __init__(self, sutunlar=None):
        self.sutunlar = sutunlar

    def fit(self, X, y=None):
        aday = KATEGORIK if self.sutunlar is None else self.sutunlar
        self.sutunlar_ = [c for c in aday if c in X.columns]
        self.kategoriler_ = {c: sorted(pd.Series(X[c]).dropna().astype(str).unique()) for c in self.sutunlar_}
        return self

    def transform(self, X):
        d = X.copy()
        for c in self.sutunlar_:
            d[c] = pd.Categorical(d[c].astype(str), categories=self.kategoriler_[c])
        return d


def hazirlik_standart(manifest, ozellikler=None):
    """Tüm algoritmaların ortak girdisi: özellik üretimi → eksik doldurma → ölçekleme / tek-sıcak.

    Doldurma ve ölçekleme yalnızca eğitim katında öğrenilir (sızıntısız)."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    sayisal = Pipeline([("doldur", SimpleImputer(strategy="median")), ("olcek", StandardScaler())])
    kategorik = Pipeline([("doldur", SimpleImputer(strategy="most_frequent")),
                          ("tek_sicak", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    sy = [c for c in SAYISAL if ozellikler is None or c in ozellikler]
    kt = [c for c in KATEGORIK if ozellikler is None or c in ozellikler]
    ct = ColumnTransformer([("sayisal", sayisal, sy), ("kategorik", kategorik, kt)])
    return Pipeline([("ozellik", OzellikUretici(bilet_sayilari=manifest)), ("donustur", ct)])


class KolonSec(BaseEstimator, TransformerMixin):
    """Özellik tablosundan sütun tutar (tut) ya da çıkarır (at). Ablasyon ve özellik deneyleri için."""

    def __init__(self, tut=None, at=None):
        self.tut = tut
        self.at = at

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.tut is not None:
            X = X[[c for c in X.columns if c in self.tut]]
        if self.at:
            X = X.drop(columns=[c for c in self.at if c in X.columns])
        return X


def lgb_dogal(manifest, tut=None, at=None, **kw):
    """LightGBM: eksik değer ve kategori doğal işlenir (doldurma / tek-sıcak yok)."""
    from lightgbm import LGBMClassifier
    from sklearn.pipeline import Pipeline
    return Pipeline([("ozellik", OzellikUretici(bilet_sayilari=manifest)), ("sec", KolonSec(tut=tut, at=at)),
                     ("kategori", KategoriDonusturucu()), ("model", LGBMClassifier(**kw))])
