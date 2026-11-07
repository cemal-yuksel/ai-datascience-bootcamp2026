"""Gün 49 · Gökyüzü sınıflandırma projesi — yardımcı işlev.

Pipeline'ın içindeki özellik mühendisliği adımı bu dosyada durur. Nedeni: `joblib` ile kaydedilen bir
Pipeline, kendi içindeki işlevleri *adıyla* hatırlar; işlev notebook'ta (`__main__`) tanımlı olursa
modeli başka bir yerde yüklemek mümkün olmaz. Modeli yüklerken bu dosyanın da yanında olması gerekir.
"""
import pandas as pd

FOTOMETRI = ["u", "g", "r", "i", "z"]                                   # beş filtredeki parlaklık (magnitüd)
RENK_CIFTLERI = [("u", "g"), ("g", "r"), ("r", "i"), ("i", "z")]          # komşu filtrelerin farkı = "renk indeksi"


def renk_indeksleri(X):
    """Girdi tablosuna dört renk indeksi (u−g, g−r, r−i, i−z) ekler. Satır bazlıdır; öğrenilen bir şey yoktur (sızıntı yok)."""
    df = pd.DataFrame(X).copy()
    for a, b in RENK_CIFTLERI:
        df[f"{a}_{b}"] = df[a] - df[b]
    return df
