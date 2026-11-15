"""Gün 54 yardımcıları: veri okuma, Türkçe adlar ve (joblib için) ayrı dosyada duran sınıflar."""
from pathlib import Path
import numpy as np
import pandas as pd

VERI_YOLU = Path(__file__).parent / "25-dry-bean.csv"

# Orijinal (Kaggle) sütun adı → Türkçe ad. "AspectRation" yazım hatası kaynakta böyle.
TR_AD = {
    "Area": "Alan", "Perimeter": "Çevre", "MajorAxisLength": "Uzun eksen", "MinorAxisLength": "Kısa eksen",
    "AspectRation": "En-boy oranı", "Eccentricity": "Basıklık (eksantriklik)", "ConvexArea": "Dışbükey alan",
    "EquivDiameter": "Eş çap", "Extent": "Kaplama oranı", "Solidity": "Doluluk", "roundness": "Yuvarlaklık",
    "Compactness": "Sıkılık", "ShapeFactor1": "Şekil 1", "ShapeFactor2": "Şekil 2",
    "ShapeFactor3": "Şekil 3", "ShapeFactor4": "Şekil 4",
}
SINIF_TR = {"SEKER": "Şeker", "BARBUNYA": "Barbunya", "BOMBAY": "Bombay", "CALI": "Çalı",
            "DERMASON": "Dermason", "HOROZ": "Horoz", "SIRA": "Sıra"}
OZELLIKLER = list(TR_AD)          # 16 ölçü (orijinal adlarla)
HEDEF = "Class"


def veri_oku(yol=None):
    """Ham veriyi okur (kopyalar dâhil); sınıf adlarını Türkçeleştirmez."""
    return pd.read_csv(yol or VERI_YOLU, encoding="utf-8-sig")


def tahmin_et(fasulye, model=None, meta=None):
    """Tek fasulye (sözlük) ya da tablo alır; tür ve olasılıkları döndürür."""
    import joblib, json
    d = Path(__file__).parent / "outputs" / "model"
    model = model or joblib.load(d / "fasulye_pca_model.joblib")
    meta = meta or json.loads((d / "meta.json").read_text(encoding="utf-8"))
    X = pd.DataFrame([fasulye]) if isinstance(fasulye, dict) else pd.DataFrame(fasulye)
    X = X[meta["ozellikler"]]
    p = model.predict_proba(X) if hasattr(model, "predict_proba") else None
    tur = model.predict(X)
    kodlar = meta["siniflar_kodlu"]                      # {"0": "Barbunya", ...}: model sayısal etiket döndürür
    out = pd.DataFrame({"Tür": [kodlar[str(int(t))] for t in tur]})
    if p is not None:
        out["Güven"] = p.max(axis=1).round(3)
    return out
