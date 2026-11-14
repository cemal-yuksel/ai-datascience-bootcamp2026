"""Sigorta primi projesi için veri okuma, özellik üretimi, model zoo'su ve hedef dönüşümü yardımcıları.

Not: joblib ile model kaydedebilmek için sınıflar notebook yerine bu dosyada durur.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin, clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import PowerTransformer, StandardScaler, PolynomialFeatures, QuantileTransformer, FunctionTransformer
from sklearn.pipeline import make_pipeline

VERI_YOLU = "24-insurance.csv"
HEDEF = "charges"
SAYISAL = ["age", "bmi", "children"]
KATEGORIK = ["sex", "smoker", "region"]


def veri_oku(yol=VERI_YOLU):
    """CSV'yi okur; ham sütunlara dokunmaz."""
    return pd.read_csv(yol)


class OzellikUretici(BaseEstimator, TransformerMixin):
    """Ham tabloyu tamamen sayısal bir tabloya çevirir (hedef kullanılmaz).

    ek=True ise iki alan bilgisi eklenir: obez (BMI >= 30) ve sigara × obez etkileşimi.
    """

    def __init__(self, ek=False):
        self.ek = ek

    def fit(self, X, y=None):
        self.bolgeler_ = sorted(X["region"].unique())
        return self

    def transform(self, X):
        d = pd.DataFrame(index=X.index)
        d["age"] = X["age"].astype(float)
        d["bmi"] = X["bmi"].astype(float)
        d["children"] = X["children"].astype(float)
        d["erkek"] = (X["sex"] == "male").astype(float)
        d["sigara"] = (X["smoker"] == "yes").astype(float)
        for b in self.bolgeler_:
            d[f"bolge_{b}"] = (X["region"] == b).astype(float)
        if self.ek:
            d["obez"] = (X["bmi"] >= 30).astype(float)
            d["sigara_x_obez"] = d["sigara"] * d["obez"]
        return d

    def get_feature_names_out(self, input_features=None):
        return np.array(self.transform(pd.DataFrame({"age": [1], "bmi": [1], "children": [0], "sex": ["male"], "smoker": ["no"], "region": [self.bolgeler_[0]]})).columns)


class SabitGuc(BaseEstimator, TransformerMixin):
    """λ'sı elle verilen Box-Cox (y > 0). λ öğrenilmez; yalnızca ortalama/sapma eğitimden öğrenilir.

    λ'yı bir «düğme» gibi taramak için kullanılır (kavram: λ=1 hiç dönüşüm yok, λ=0 logaritma).
    """

    def __init__(self, lam=0.0):
        self.lam = lam

    def _bc(self, x):
        from scipy.special import boxcox
        return boxcox(x, self.lam)

    def fit(self, X, y=None):
        z = self._bc(np.asarray(X, dtype=float))
        self.mu_, self.sd_ = z.mean(axis=0), z.std(axis=0)
        return self

    def transform(self, X):
        return (self._bc(np.asarray(X, dtype=float)) - self.mu_) / self.sd_

    def inverse_transform(self, Z):
        w = np.asarray(Z, dtype=float) * self.sd_ + self.mu_
        lam = self.lam
        if abs(lam) < 1e-12:
            return np.exp(np.clip(w, None, 50))
        sinir = -1.0 / lam            # 1 + λw > 0 olmalı; aşan tahminleri sınıra çekiyoruz (modelin saçmalamasına karşı emniyet)
        w = np.minimum(w, sinir - 1e-6) if lam < 0 else np.maximum(w, sinir + 1e-6)
        return np.power(lam * w + 1.0, 1.0 / lam)


def olc(y, p):
    """Dört ölçüt: RMSE ($), MAE ($), R², RMSLE (göreli hata). Negatif tahminler RMSLE için 0'a kırpılır."""
    y = np.asarray(y, float); p = np.asarray(p, float)
    rmse = float(np.sqrt(np.mean((y - p) ** 2)))
    mae = float(np.mean(np.abs(y - p)))
    r2 = float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2))
    rmsle = float(np.sqrt(np.mean((np.log1p(np.clip(p, 0, None)) - np.log1p(y)) ** 2)))
    return {"RMSE": rmse, "MAE": mae, "R2": r2, "RMSLE": rmsle}


def hedef_donusturucu(ad):
    """Hedef için dönüşüm seçenekleri. Hepsi standardize eder, böylece ölçek farkı yarışa karışmaz."""
    if ad == "ham":
        return StandardScaler()
    if ad == "box-cox":
        return PowerTransformer(method="box-cox", standardize=True)
    if ad == "yeo-johnson":
        return PowerTransformer(method="yeo-johnson", standardize=True)
    if ad == "log":
        return make_pipeline(FunctionTransformer(np.log, np.exp, validate=True), StandardScaler())
    if ad == "karekök":
        return make_pipeline(FunctionTransformer(np.sqrt, np.square, validate=True), StandardScaler())
    if ad == "kantil":
        return QuantileTransformer(n_quantiles=200, output_distribution="normal", random_state=42)
    if isinstance(ad, (int, float)):
        return SabitGuc(lam=float(ad))
    raise ValueError(ad)


def hedefli(model, ad="box-cox"):
    """Modeli hedef dönüşümüyle sarar; λ her fit'te yalnızca eğitim hedefinden öğrenilir."""
    return TransformedTargetRegressor(regressor=model, transformer=hedef_donusturucu(ad), check_inverse=False)


class BoxCoxSmearing(BaseEstimator, RegressorMixin):
    """Box-Cox hedefli regresör + «smearing» düzeltmesi.

    Ters dönüşüm ortancaya yakın tahmin verir. Eğitim artıklarını (dönüşmüş uzayda) tahmine ekleyip
    ters dönüştürerek ortalamayı tahmin ederiz: ŷ = mean_i( f⁻¹(ẑ + e_i) ).
    """

    def __init__(self, model=None, duzelt=True, ornek=200):
        self.model = model
        self.duzelt = duzelt
        self.ornek = ornek

    def fit(self, X, y):
        self.pt_ = PowerTransformer(method="box-cox", standardize=True).fit(np.asarray(y).reshape(-1, 1))
        z = self.pt_.transform(np.asarray(y).reshape(-1, 1)).ravel()
        self.model_ = clone(self.model).fit(X, z)
        # artıklar: hatayı gerçekçi görmek için çapraz doğrulamalı artık (aşırı uyum yapmasın)
        from sklearn.model_selection import cross_val_predict
        zt = cross_val_predict(clone(self.model), X, z, cv=5)
        self.art_ = (z - zt)
        rng = np.random.RandomState(0)
        self.art_ornek_ = rng.choice(self.art_, size=min(self.ornek, len(self.art_)), replace=False)
        return self

    def predict(self, X):
        z = self.model_.predict(X)
        if not self.duzelt:
            return self.pt_.inverse_transform(z.reshape(-1, 1)).ravel()
        M = z[:, None] + self.art_ornek_[None, :]
        ters = self.pt_.inverse_transform(M.reshape(-1, 1)).reshape(M.shape)
        return np.nanmean(ters, axis=1)


# ── Model zoo'su ─────────────────────────────────────────────────────────────
def model_zoo(rs=42, hizli=True):
    """(ad → (tahminci, ölçekleme_gerekli_mi)) sözlüğü. 27 algoritma + taban."""
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import (LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge, HuberRegressor, SGDRegressor, RANSACRegressor)
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.svm import SVR
    from sklearn.kernel_ridge import KernelRidge
    from sklearn.neural_network import MLPRegressor
    from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
    from sklearn.ensemble import (BaggingRegressor, RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor,
                                  HistGradientBoostingRegressor, AdaBoostRegressor)
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as C
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from catboost import CatBoostRegressor

    z = {
        "Taban (ortalama)": (DummyRegressor(strategy="mean"), False),
        "Doğrusal regresyon": (LinearRegression(), True),
        "Ridge": (Ridge(alpha=1.0), True),
        "Lasso": (Lasso(alpha=0.01, max_iter=20000), True),
        "ElasticNet": (ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=20000), True),
        "Bayes Ridge": (BayesianRidge(), True),
        "Huber": (HuberRegressor(max_iter=1000), True),
        "RANSAC": (RANSACRegressor(random_state=rs), True),
        "SGD regresör": (SGDRegressor(random_state=rs, max_iter=2000, tol=1e-4), True),
        "Polinom(2) + Ridge": (make_pipeline(PolynomialFeatures(2, include_bias=False), Ridge(alpha=1.0)), True),
        "KNN": (KNeighborsRegressor(n_neighbors=10, weights="distance"), True),
        "SVR (RBF)": (SVR(C=3.0, epsilon=0.05), True),
        "Çekirdek Ridge (RBF)": (KernelRidge(alpha=0.5, kernel="rbf", gamma=0.05), True),
        "Gauss süreci": (GaussianProcessRegressor(kernel=C(1.0) * RBF(length_scale=2.0) + WhiteKernel(0.3), normalize_y=True, random_state=rs), True),
        "MLP": (MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=800, early_stopping=True, random_state=rs), True),
        "Karar ağacı": (DecisionTreeRegressor(max_depth=6, min_samples_leaf=10, random_state=rs), False),
        "Extra tree (tek)": (ExtraTreeRegressor(max_depth=8, min_samples_leaf=8, random_state=rs), False),
        "Bagging (ağaç)": (BaggingRegressor(DecisionTreeRegressor(min_samples_leaf=5), n_estimators=100, random_state=rs, n_jobs=1), False),
        "Rastgele orman": (RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=rs, n_jobs=1), False),
        "Extra trees": (ExtraTreesRegressor(n_estimators=300, min_samples_leaf=4, random_state=rs, n_jobs=1), False),
        "Gradient Boosting": (GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=3, random_state=rs), False),
        "HistGradientBoosting": (HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=20, random_state=rs), False),
        "AdaBoost": (AdaBoostRegressor(DecisionTreeRegressor(max_depth=4), n_estimators=150, learning_rate=0.5, random_state=rs), False),
        "XGBoost": (XGBRegressor(n_estimators=250, learning_rate=0.04, max_depth=3, subsample=0.8, colsample_bytree=0.9, random_state=rs, n_jobs=1, verbosity=0), False),
        "LightGBM": (LGBMRegressor(n_estimators=250, learning_rate=0.04, num_leaves=8, min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.9, random_state=rs, n_jobs=1, verbose=-1), False),
        "CatBoost": (CatBoostRegressor(iterations=400, learning_rate=0.05, depth=4, random_seed=rs, verbose=0, thread_count=1), False),
    }
    return z


def topluluklar(rs=42):
    from sklearn.ensemble import StackingRegressor, VotingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.svm import SVR
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    taban = [("ridge", make_pipeline(StandardScaler(), Ridge(1.0))), ("svr", make_pipeline(StandardScaler(), SVR(C=3.0, epsilon=0.05))),
             ("gb", GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=3, random_state=rs)),
             ("rf", RandomForestRegressor(n_estimators=150, min_samples_leaf=5, random_state=rs, n_jobs=1))]
    return {"Oylama (4 model)": VotingRegressor(taban), "Yığın (Ridge meta)": StackingRegressor(taban, final_estimator=Ridge(1.0), cv=5)}


def boru_hatti(ad, tahminci, olcek, ek=True, hedef="box-cox", yj_ozellik=False):
    """Özellik üretici → (ölçekleyici) → model → hedef dönüşümü zinciri."""
    adimlar = [OzellikUretici(ek=ek)]
    if olcek:
        adimlar.append(PowerTransformer(method="yeo-johnson", standardize=True) if yj_ozellik else StandardScaler())
    adimlar.append(clone(tahminci))
    return hedefli(make_pipeline(*adimlar), hedef)


class KolonKapat(BaseEstimator, TransformerMixin):
    """Ablasyon için: seçilen ham sütunları sabit bir değerle değiştirir (bilgiyi öldürür).

    Sayısal sütun → eğitim ortancası, kategorik sütun → en sık değer.
    """

    def __init__(self, sutunlar=()):
        self.sutunlar = sutunlar

    def fit(self, X, y=None):
        self.sabit_ = {}
        for c in self.sutunlar:
            self.sabit_[c] = X[c].median() if pd.api.types.is_numeric_dtype(X[c]) else X[c].mode().iloc[0]
        return self

    def transform(self, X):
        X = X.copy()
        for c, v in self.sabit_.items():
            X[c] = v
        return X


def aralik_hesapla(model, X, y, q=(0.05, 0.95), cv=5, rs=0, tf=None):
    """Çapraz doğrulamalı artıklardan, DÖNÜŞMÜŞ uzayda artık kantilleri çıkarır.

    Dönüşmüş uzayda simetrik bir bant, dolar uzayında (hedef çarpıksa) asimetrik bir banda dönüşür.
    """
    from sklearn.model_selection import KFold, cross_val_predict
    oof = cross_val_predict(clone(model), X, y, cv=KFold(cv, shuffle=True, random_state=rs))
    m = clone(model).fit(X, y)
    tf = clone(tf if tf is not None else m.transformer_).fit(np.asarray(y, float).reshape(-1, 1))   # bant dönüşümü, modelin hedef dönüşümünden bağımsız seçilebilir
    z_gercek = tf.transform(np.asarray(y, float).reshape(-1, 1)).ravel()
    z_tahmin = tf.transform(np.clip(oof, 1.0, None).reshape(-1, 1)).ravel()
    e = z_gercek - z_tahmin
    return {"model": m, "tf": tf, "q_alt": float(np.quantile(e, q[0])), "q_ust": float(np.quantile(e, q[1])), "oof": oof,
            "artik_dolar": (np.asarray(y, float) - oof)}


def tahmin_araligi(paket, X):
    """Paket: aralik_hesapla çıktısı. Nokta tahmin + dönüşmüş uzayda kurulan %90 aralık (dolar)."""
    m = paket["model"]; tf = paket["tf"]
    p = m.predict(X)
    z = tf.transform(np.clip(p, 1.0, None).reshape(-1, 1)).ravel()
    alt = tf.inverse_transform((z + paket["q_alt"]).reshape(-1, 1)).ravel()
    ust = tf.inverse_transform((z + paket["q_ust"]).reshape(-1, 1)).ravel()
    return pd.DataFrame({"tahmin": p, "alt": alt, "ust": ust}, index=X.index)


GECERLI_ARALIK = {"age": (18, 64), "bmi": (14, 60), "children": (0, 6)}
GECERLI_SINIF = {"sex": {"male", "female"}, "smoker": {"yes", "no"}, "region": {"northeast", "northwest", "southeast", "southwest"}}


def girdi_dogrula(X):
    """Üretimde yanlış girdiyi erken yakalar."""
    eksik = set(SAYISAL + KATEGORIK) - set(X.columns)
    if eksik:
        raise ValueError(f"Eksik sütun: {sorted(eksik)}")
    for c, (lo, hi) in GECERLI_ARALIK.items():
        if X[c].isna().any() or X[c].lt(lo).any() or X[c].gt(hi).any():
            raise ValueError(f"{c} beklenen aralık dışında ({lo}–{hi}) ya da boş")
    for c, k in GECERLI_SINIF.items():
        if not set(X[c].unique()) <= k:
            raise ValueError(f"{c} için tanımsız sınıf: {set(X[c].unique()) - k}")
    return X[SAYISAL + KATEGORIK]
