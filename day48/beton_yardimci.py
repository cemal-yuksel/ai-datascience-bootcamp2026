"""Gün 48 · Beton dayanımı projesi — yardımcı işlev.

Pipeline'ın içindeki özellik mühendisliği adımı bu dosyada durur. Nedeni: `joblib` ile kaydedilen bir
Pipeline, kendi içindeki işlevleri *adıyla* hatırlar; işlev notebook'ta (`__main__`) tanımlı olursa
modeli başka bir yerde yüklemek mümkün olmaz. Modeli yüklerken bu dosyanın da yanında olması gerekir.
"""
import numpy as np
import pandas as pd

HAM_OZELLIKLER = ["cimento", "curuf", "kul", "su", "akiskanlastirici", "iri_agrega", "ince_agrega", "yas_gun"]


def muhendislik(X):
    """Ham 8 sütundan beton teknolojisine dayalı 5 ek özellik üretir (satır bazlı, sızıntı yok)."""
    df = pd.DataFrame(X, columns=HAM_OZELLIKLER).copy()
    baglayici = df["cimento"] + df["curuf"] + df["kul"]              # toplam bağlayıcı (çimento + cüruf + kül)
    df["su_cimento"] = df["su"] / df["cimento"]                       # su/çimento oranı (Abrams yasasının anahtarı)
    df["su_baglayici"] = df["su"] / baglayici                         # su/bağlayıcı oranı
    df["baglayici"] = baglayici
    df["log_yas"] = np.log(df["yas_gun"])                             # dayanım yaşla logaritmik artar
    df["agrega_orani"] = df["iri_agrega"] / (df["iri_agrega"] + df["ince_agrega"])
    return df
