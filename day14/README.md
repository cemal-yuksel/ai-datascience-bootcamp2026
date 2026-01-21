<div align="center">

```text
    ███████╗ ██████╗ ██╗              ██╗ ██████╗ ██╗███╗   ██╗███████╗
    ██╔════╝██╔═══██╗██║         ██  ██║██╔═══██╗██║████╗  ██║██╔════╝
    ███████╗██║   ██║██║         ╚█████╔╝██║   ██║██║██╔██╗ ██║███████╗
    ╚════██║██║▄▄ ██║██║          ╚═══██╗██║   ██║██║██║╚██╗██║╚════██║
    ███████║╚██████╔╝███████╗         ██║╚██████╔╝██║██║ ╚████║███████║
    ╚══════╝ ╚══▀▀═╝ ╚══════╝         ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝
                                                                        
    ███████╗██████╗  ██████╗ ███╗   ███╗    ███████╗███████╗██████╗  ██████╗ 
    ██╔════╝██╔══██╗██╔═══██╗████╗ ████║    ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗
    █████╗  ██████╔╝██║   ██║██╔████╔██║      ███╔╝ █████╗  ██████╔╝██║   ██║
    ██╔══╝  ██╔══██╗██║   ██║██║╚██╔╝██║     ███╔╝  ██╔══╝  ██╔══██╗██║   ██║
    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║    ███████╗███████╗██║  ██║╚██████╔╝
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ 
                                                                               
          ████████╗ ██████╗     ██╗  ██╗███████╗██████╗  ██████╗              
          ╚══██╔══╝██╔═══██╗    ██║  ██║██╔════╝██╔══██╗██╔═══██╗             
             ██║   ██║   ██║    ███████║█████╗  ██████╔╝██║   ██║             
             ██║   ██║   ██║    ██╔══██║██╔══╝  ██╔══██╗██║   ██║             
             ██║   ╚██████╔╝    ██║  ██║███████╗██║  ██║╚██████╔╝             
             ╚═╝    ╚═════╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝              
```

### 🎓 YBS Öğrencileri İçin Kapsamlı SQL JOIN Eğitimi

**From Zero to Hero | Görselleştirmeler ile İnteraktif Öğrenme**

---

[![Python](https://img.shields.io/badge/Python-3.8+-4a7c7e.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-003b57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626.svg?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)
[![License](https://img.shields.io/badge/License-Educational-8b7355.svg?style=for-the-badge)](LICENSE)

</div>

---

## 🌟 Genel Bakış

Bu proje, **SQL JOIN işlemlerini** temellerden ileri seviyeye öğretmek için tasarlanmış **kapsamlı bir Jupyter Notebook eğitim materyalidir**. YBS (Yönetim Bilişim Sistemleri) öğrencileri ve veri analizcileri için gerçek iş senaryoları ile zenginleştirilmiş, görsel diyagramlar ve interaktif örnekler içerir.

### 🎯 Neden Bu Eğitim?

<table>
<tr>
<td width="50%" valign="top">

**📚 Eğitim Özellikleri**
- ✅ **6 farklı JOIN türü** detaylı açıklamalar ile
- ✅ **Görsel Venn diyagramları** ve SVG illüstrasyonlar
- ✅ **YBS perspektifiyle** gerçek iş senaryoları
- ✅ **İnteraktif HTML tablolar** ve renkli çıktılar
- ✅ **SQLite3 + Pandas** entegre kullanım
- ✅ **Best practices** ve sık yapılan hatalar

</td>
<td width="50%" valign="top">

**🎓 Öğrenme Çıktıları**
- ✅ Veritabanı normalizasyonu kavramı
- ✅ Primary Key ve Foreign Key ilişkileri
- ✅ Her JOIN türünün kullanım senaryoları
- ✅ SQL sorgu optimizasyonu teknikleri
- ✅ Pandas ile SQL entegrasyonu
- ✅ Gerçek dünya veri analizi becerileri

</td>
</tr>
</table>

### 🎭 6 JOIN Türü

Bu eğitimde öğrenecekleriniz:

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#87CEEB','primaryTextColor':'#2d3436','lineColor':'#95a5a6','fontSize':'16px'}}}%%
mindmap
  root((🔗 SQL<br/>JOINS))
    INNER JOIN
      ⚡ En çok kullanılan
      🎯 Kesişim kayıtları
      💼 Satış raporları
    LEFT JOIN
      ⬅️ Sol tablo önceliği
      📊 Eksik kayıt analizi
      🔍 Müşteri aktivitesi
    RIGHT JOIN
      ➡️ Sağ tablo önceliği
      🔄 LEFT JOIN tersi
      ⚠️ SQLite desteklemez
    FULL OUTER JOIN
      🌐 Tüm kayıtlar
      📋 Veri tutarsızlığı
      🔎 Uyumsuzluk tespiti
    CROSS JOIN
      ✖️ Kartezyen çarpım
      🎲 Kombinasyon analizi
      ⚠️ Büyük veri dikkat
    SELF JOIN
      🪞 Kendisiyle birleşme
      👥 Hiyerarşik yapılar
      🏢 Çalışan-Yönetici
```

---

## 📂 Proje Yapısı

```
day14/
│
├── 📓 sqljoins.ipynb                  # Ana eğitim notebook'u (4560+ satır)
├── 📄 README.md                       # Bu dosya
└── 🗄️ joins_example.db               # SQLite veritabanı (runtime'da oluşur)
```

### 📓 Notebook Yapısı

| Bölüm | İçerik | Hücre Sayısı |
|-------|--------|--------------|
| 🌟 **Giriş** | Motivasyon, JOIN'in önemi, terminoloji | 6 hücre |
| 🛠️ **Ortam Hazırlığı** | Veritabanı oluşturma, örnek veri | 8 hücre |
| ⚡ **INNER JOIN** | Teori, örnekler, iş senaryoları | 10 hücre |
| ⬅️ **LEFT JOIN** | Açıklama, kullanım alanları, pratikler | 8 hücre |
| ➡️ **RIGHT JOIN** | SQLite alternatifi, emülasyon | 6 hücre |
| 🔄 **FULL OUTER JOIN** | Simülasyon, UNION kullanımı | 8 hücre |
| ✖️ **CROSS JOIN** | Kartezyen çarpım, dikkat edilecekler | 6 hücre |
| 🪞 **SELF JOIN** | Hiyerarşik yapılar, recursive sorgular | 8 hücre |
| 🎯 **İleri Düzey** | Multiple joins, subqueries, optimizasyon | 10 hücre |

---

## 🎓 Eğitim Hedefleri

<div align="center">

| 🎯 Hedef | 📝 Açıklama | ✅ Başarı Kriteri |
|----------|-------------|-------------------|
| **JOIN Kavramı** | SQL JOIN'in ne olduğunu ve neden önemli olduğunu anlamak | Normalizasyon ve JOIN ilişkisini açıklayabilme |
| **Tüm JOIN Türleri** | 6 farklı JOIN türünü teorik ve pratik olarak öğrenmek | Her JOIN türü için doğru kullanım senaryosunu belirleme |
| **YBS Perspektifi** | İş dünyasındaki gerçek senaryolarla uygulamalı öğrenme | İş problemi için uygun JOIN stratejisi geliştirebilme |
| **Best Practices** | SQL sorgu optimizasyonu ve yaygın hataları önleme | Performanslı ve okunabilir sorgular yazabilme |
| **Pandas Entegrasyonu** | SQL ve Pandas'ı birlikte kullanma | Veritabanından Pandas'a veri çekip analiz edebilme |

</div>

---

## 📊 JOIN Türleri - Detaylı Açıklama

### ⚡ INNER JOIN

En yaygın kullanılan JOIN türüdür. **Sadece her iki tabloda da eşleşen kayıtları** döndürür.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#c62828','primaryTextColor':'#fff','lineColor':'#1976d2'}}}%%
graph LR
    A[👥 Müşteriler<br/>Tablosu] -->|musteri_id| C{INNER JOIN}
    B[📦 Siparişler<br/>Tablosu] -->|musteri_id| C
    C --> D[📊 Sonuç:<br/>Sadece sipariş<br/>veren müşteriler]
    
    style A fill:#87CEEB,stroke:#6495ED,stroke-width:3px,color:#2d3436
    style B fill:#FFB6C1,stroke:#FF69B4,stroke-width:3px,color:#2d3436
    style C fill:#c62828,stroke:#d32f2f,stroke-width:4px,color:#fff
    style D fill:#98D98E,stroke:#90EE90,stroke-width:3px,color:#2d3436
```

**💼 Kullanım Senaryoları:**
- Satış raporları (Müşteri + Sipariş)
- Stok analizi (Ürün + Tedarikçi)
- Çalışan departman listesi (Çalışan + Departman)

**🎯 Avantajlar:**
- Sadece ilgili kayıtları getirir
- Performans açısından optimize
- NULL değerlerle uğraşmaya gerek yok

**⚠️ Dezavantajlar:**
- Eşleşmeyen kayıtlar kaybolur
- Eksik veri analizinde kullanılamaz

---

### ⬅️ LEFT JOIN (LEFT OUTER JOIN)

Sol tablodaki **tüm kayıtları** döndürür, sağ tabloda eşleşme varsa ekler, yoksa **NULL** döner.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#558b2f','primaryTextColor':'#fff','lineColor':'#1976d2'}}}%%
graph LR
    A[👥 Tüm Müşteriler<br/>1000 kayıt] -->|musteri_id| C{LEFT JOIN}
    B[📦 Siparişler<br/>750 eşleşme] -->|musteri_id| C
    C --> D[📊 Sonuç: 1000 kayıt<br/>✅ 750 sipariş veren<br/>❌ 250 sipariş vermeyen]
    
    style A fill:#558b2f,stroke:#689f38,stroke-width:4px,color:#fff
    style B fill:#FFE5B4,stroke:#FFD700,stroke-width:2px,color:#2d3436
    style C fill:#558b2f,stroke:#689f38,stroke-width:4px,color:#fff
    style D fill:#f1f8e9,stroke:#558b2f,stroke-width:3px,color:#2d3436
```

**💼 Kullanım Senaryoları:**
- Sipariş vermeyen müşterileri bulma
- Satın alma yapmayan ürünleri tespit etme
- Eksik kayıt analizi

**🎯 Avantajlar:**
- Sol tablonun bütünlüğü korunur
- Eksik kayıtları tespit edebilme
- Veri kaybı olmaz

**⚠️ Dikkat:**
- Sağ taraf NULL'lar içerebilir
- NULL kontrolü gerektirir

---

### ➡️ RIGHT JOIN (RIGHT OUTER JOIN)

Sağ tablodaki **tüm kayıtları** döndürür. LEFT JOIN'in tam tersidir.

> **⚠️ ÖNEMLİ NOT:** SQLite **RIGHT JOIN'i desteklemez**. Bu eğitimde LEFT JOIN ile nasıl emüle edileceği gösterilmektedir.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#0277bd','primaryTextColor':'#fff'}}}%%
graph LR
    A[👥 Müşteriler] -->|musteri_id| C{RIGHT JOIN}
    B[📦 Tüm Siparişler<br/>Sağ tablo öncelikli] -->|musteri_id| C
    C --> D[📊 Tüm siparişler<br/>+ müşteri bilgisi<br/>varsa]
    
    style A fill:#B0D4E3,stroke:#87CEEB,stroke-width:2px,color:#2d3436
    style B fill:#0277bd,stroke:#01579b,stroke-width:4px,color:#fff
    style C fill:#0277bd,stroke:#01579b,stroke-width:4px,color:#fff
    style D fill:#e1f5fe,stroke:#0277bd,stroke-width:3px,color:#2d3436
```

**💡 SQLite'ta Alternatif:**
```sql
-- RIGHT JOIN (desteklenmez)
SELECT * FROM A RIGHT JOIN B ON A.id = B.id

-- LEFT JOIN ile eşdeğer
SELECT * FROM B LEFT JOIN A ON B.id = A.id
```

---

### 🔄 FULL OUTER JOIN

Her iki tablodaki **tüm kayıtları** döndürür. Eşleşmeyen kayıtlar NULL ile doldurulur.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#c2185b','primaryTextColor':'#fff'}}}%%
graph TB
    A[👥 Müşteriler<br/>850 kayıt] --> C{FULL OUTER<br/>JOIN}
    B[📦 Siparişler<br/>920 kayıt] --> C
    C --> D[📊 Sonuç: Tüm veriler<br/>✅ Eşleşenler<br/>❌ Sol NULL<br/>❌ Sağ NULL]
    
    style A fill:#c2185b,stroke:#d81b60,stroke-width:3px,color:#fff
    style B fill:#c2185b,stroke:#d81b60,stroke-width:3px,color:#fff
    style C fill:#c2185b,stroke:#d81b60,stroke-width:4px,color:#fff
    style D fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#2d3436
```

**💼 Kullanım Senaryoları:**
- Veri tutarsızlığı analizi
- Uyumsuz kayıtları bulma
- Veri kalitesi kontrolü

**🎯 SQLite'ta Implementasyon:**
```sql
-- UNION ile simülasyon
SELECT * FROM A LEFT JOIN B ON A.id = B.id
UNION
SELECT * FROM A RIGHT JOIN B ON A.id = B.id
```

> **⚠️ NOT:** SQLite FULL OUTER JOIN'i desteklemez, UNION ile emüle edilir.

---

### ✖️ CROSS JOIN (Kartezyen Çarpım)

Her iki tablonun **her satırını birbirleriyle eşleştirir**. Sonuç = A satır sayısı × B satır sayısı

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#f57f17','primaryTextColor':'#2d3436'}}}%%
graph LR
    A[🎨 Renkler<br/>5 kayıt] -->|×| C{CROSS<br/>JOIN}
    B[📐 Bedenler<br/>4 kayıt] -->|×| C
    C --> D[📊 Sonuç<br/>5 × 4 = 20<br/>kombinasyon]
    
    style A fill:#ffe082,stroke:#f57f17,stroke-width:3px,color:#2d3436
    style B fill:#ffe082,stroke:#f57f17,stroke-width:3px,color:#2d3436
    style C fill:#f57f17,stroke:#f9a825,stroke-width:4px,color:#fff
    style D fill:#fff8e1,stroke:#f57f17,stroke-width:3px,color:#2d3436
```

**💼 Kullanım Senaryoları:**
- Ürün kombinasyonları (renk × beden)
- Takvim tabloları (yıl × ay × gün)
- Test veri setleri oluşturma

**⚠️ DİKKAT EDİLMESİ GEREKENLER:**
- 🚨 Satır sayısı hızla patlar!
- 🚨 1000 × 1000 = 1,000,000 satır
- 🚨 Performans sorunu yaratabilir
- ✅ WHERE ile filtreleyin

---

### 🪞 SELF JOIN

Bir tablo **kendisiyle JOIN** edilir. Hiyerarşik yapılar için idealdir.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#7b1fa2','primaryTextColor':'#fff'}}}%%
graph TB
    A[👤 Çalışanlar Tablosu<br/>id, ad, yonetici_id] --> C{SELF JOIN}
    A --> C
    C --> D[📊 Sonuç:<br/>Çalışan + Yönetici<br/>bilgileri birlikte]
    
    E[id=1, Ahmet, yonetici_id=NULL] --> F[Patron]
    G[id=2, Mehmet, yonetici_id=1] --> H[Çalışan → Ahmet]
    
    style A fill:#7b1fa2,stroke:#8e24aa,stroke-width:3px,color:#fff
    style C fill:#7b1fa2,stroke:#8e24aa,stroke-width:4px,color:#fff
    style D fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#2d3436
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#2d3436
    style F fill:#7b1fa2,stroke:#8e24aa,stroke-width:2px,color:#fff
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#2d3436
    style H fill:#ce93d8,stroke:#ab47bc,stroke-width:2px,color:#2d3436
```

**💼 Kullanım Senaryoları:**
- Çalışan-Yönetici ilişkisi
- Ürün kategorileri (ana kategori - alt kategori)
- Organizasyon şemaları
- Aile ağaçları

**🎯 Önemli Nokta:**
- Tablo iki farklı **alias** ile kullanılır (e1, e2)
- Sonsuz döngüden kaçının
- Recursive yapılar için CTE kullanın

---

## 🛠️ Teknoloji Stack

| Teknoloji | Versiyon | Kullanım Amacı |
|-----------|----------|----------------|
| **Python** | 3.8+ | Ana programlama dili |
| **SQLite3** | 3.0+ | Hafif dosya tabanlı veritabanı |
| **Pandas** | 2.0+ | Veri manipülasyonu ve analiz |
| **Jupyter** | Latest | İnteraktif notebook ortamı |
| **Matplotlib** | 3.0+ | (Opsiyonel) Veri görselleştirme |

---

## 🚀 Kurulum ve Çalıştırma

### 📋 Gereksinimler

```bash
# Python 3.8 veya üzeri gereklidir
python --version

# Gerekli kütüphaneler
pip install pandas jupyter notebook
```

> **💡 NOT:** SQLite3 Python'a gömülüdür, ayrıca kurulum gerekmez!

### ▶️ Notebook'u Çalıştırma

1. **Repository'yi klonlayın veya dosyayı indirin**
   ```bash
   cd day14
   ```

2. **Jupyter Notebook'u başlatın**
   ```bash
   jupyter notebook sqljoins.ipynb
   ```

3. **Hücreleri sırayla çalıştırın**
   - `Shift + Enter` ile hücre çalıştırma
   - `Cell > Run All` ile tümünü çalıştırma

### 📁 Veritabanı Oluşturma

Notebook çalıştığında otomatik olarak `joins_example.db` dosyası oluşturulur ve örnek verilerle doldurulur:

- 👥 **Customers** (Müşteriler)
- 📦 **Orders** (Siparişler)
- 🏢 **Employees** (Çalışanlar)
- 📊 **Products** (Ürünler)
- 🎨 **Colors** (Renkler)
- 📐 **Sizes** (Bedenler)

---

## 💼 Gerçek Dünya Kullanım Senaryoları

### 🎯 Senaryo 1: Satış Raporu Oluşturma

**İş İhtiyacı:** Müşteri adı, sipariş tarihi ve ürün bilgilerini içeren satış raporu

**Kullanılan JOIN:**
- Customers ⚡ INNER JOIN Orders
- Orders ⚡ INNER JOIN Products

**Çıktı:** Satış yapan müşteriler, siparişleri ve ürün detayları

---

### 🎯 Senaryo 2: Aktif Olmayan Müşterileri Bulma

**İş İhtiyacı:** Hiç sipariş vermemiş müşterileri pazarlama kampanyası için tespit etme

**Kullanılan JOIN:**
- Customers ⬅️ LEFT JOIN Orders
- WHERE Orders.id IS NULL

**Çıktı:** Sipariş vermeyen müşteri listesi

---

### 🎯 Senaryo 3: Organizasyon Şeması

**İş İhtiyacı:** Her çalışanın kim olduğunu ve yöneticisinin kim olduğunu gösterme

**Kullanılan JOIN:**
- Employees 🪞 SELF JOIN Employees

**Çıktı:** Çalışan - Yönetici eşleşmeleri

---

### 🎯 Senaryo 4: Ürün Varyasyon Matrisi

**İş İhtiyacı:** E-ticaret sitesi için tüm renk-beden kombinasyonlarını oluşturma

**Kullanılan JOIN:**
- Colors ✖️ CROSS JOIN Sizes

**Çıktı:** Tüm olası ürün varyasyonları

---

## 📈 Öğrenme Yol Haritası

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#667eea','primaryTextColor':'#fff','lineColor':'#95a5a6','fontSize':'14px'}}}%%
graph TB
    START[🎯 Başlangıç] --> A[📚 1. Temel Kavramlar]
    A --> A1[Primary Key]
    A --> A2[Foreign Key]
    A --> A3[Normalizasyon]
    
    A1 --> B[⚡ 2. INNER JOIN]
    A2 --> B
    A3 --> B
    
    B --> B1[Teori + Örnekler]
    B1 --> B2[İş Senaryoları]
    B2 --> C[⬅️ 3. LEFT JOIN]
    
    C --> C1[NULL Yönetimi]
    C1 --> C2[Eksik Kayıt Analizi]
    C2 --> D{📊 Pratik<br/>Yaptınız mı?}
    
    D -->|Evet| E[🔄 4. FULL OUTER JOIN]
    D -->|Hayır| C
    
    E --> E1[UNION Kullanımı]
    E1 --> F[✖️ 5. CROSS JOIN]
    
    F --> F1[⚠️ Performans Dikkat]
    F1 --> G[🪞 6. SELF JOIN]
    
    G --> G1[Hiyerarşik Yapılar]
    G1 --> H[🚀 7. İleri Düzey]
    
    H --> H1[Multiple JOINs]
    H --> H2[Subqueries]
    H --> H3[Optimizasyon]
    
    H1 --> END[🎓 Tebrikler!<br/>SQL JOIN Master]
    H2 --> END
    H3 --> END
    
    style START fill:#667eea,stroke:#764ba2,stroke-width:3px,color:#fff
    style END fill:#2dce89,stroke:#2dcecc,stroke-width:4px,color:#fff
    style A fill:#5e72e4,stroke:#825ee4,stroke-width:2px,color:#fff
    style B fill:#c62828,stroke:#d32f2f,stroke-width:2px,color:#fff
    style C fill:#558b2f,stroke:#689f38,stroke-width:2px,color:#fff
    style D fill:#f57f17,stroke:#f9a825,stroke-width:3px,color:#fff
    style E fill:#c2185b,stroke:#d81b60,stroke-width:2px,color:#fff
    style F fill:#f57f17,stroke:#f9a825,stroke-width:2px,color:#fff
    style G fill:#7b1fa2,stroke:#8e24aa,stroke-width:2px,color:#fff
    style H fill:#0277bd,stroke:#01579b,stroke-width:2px,color:#fff
```

---

## 🎯 Best Practices ve İpuçları

### ✅ Yapılması Gerekenler

| 🎯 Kural | 📝 Açıklama |
|----------|-------------|
| **İndeks Kullanın** | JOIN anahtarları üzerinde index oluşturun |
| **Alias Kullanın** | Tablo adlarını kısaltın (t1, t2) |
| **WHERE Filtreleyin** | JOIN öncesi gereksiz satırları filtreleyin |
| **SELECT Spesifik** | `SELECT *` yerine gerekli sütunları belirtin |
| **JOIN Sırası** | Küçük tablolarla başlayın |

### ❌ Yapılmaması Gerekenler

| ⚠️ Hata | 📝 Sonuç |
|---------|----------|
| **CROSS JOIN Kontrolsüz** | Milyonlarca satır üretebilir |
| **NULL Kontrolsüz LEFT JOIN** | Beklenmeyen sonuçlar |
| **İndeks Olmadan Büyük JOIN** | Performans felaketi |
| **Gereksiz FULL OUTER** | Yavaş ve verimsiz |
| **SELF JOIN Sonsuz Döngü** | Stack overflow |

---

## 📚 Ek Kaynaklar

### 📖 Önerilen Okumalar

- [SQLite Official Documentation](https://www.sqlite.org/docs.html)
- [Pandas SQL Integration](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
- [SQL JOIN Visualizer](https://sql-joins.leopard.in.ua/)
- [Database Normalization Guide](https://www.guru99.com/database-normalization.html)

### 🎥 Video Kaynakları

- Khan Academy - SQL Basics
- Coursera - Database Management Essentials
- YouTube - SQL JOIN Tutorial by freeCodeCamp

---

## 🤝 Katkıda Bulunma

Bu eğitim materyali **Veri Bilimi ve Makine Öğrenmesi 2026 - 100 Günlük Bootcamp** programının bir parçasıdır.

### 💡 Önerileriniz

- Hata bulursanız issue açın
- Yeni örnekler eklemek isterseniz pull request gönderin
- Sorularınız için discussions kullanın

---

## 📝 Lisans

Bu proje eğitim amaçlı hazırlanmıştır. Kaynak göstererek kullanabilirsiniz.

---

<div align="center">

### 🎓 İyi Öğrenmeler Dileriz!

**Sorularınız için:** GitHub Discussions  
**Güncellemeler için:** Repository'yi ⭐ işaretleyin

---

**Made with ❤️ by Cemal YÜKSEL for YBS Students**

</div>
