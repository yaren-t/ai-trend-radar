# AI Trend Radar

Türkçe teknoloji ve yazılım yayınlarının RSS akışlarını tarayarak **Yapay Zeka (AI)** odaklı haberleri otomatik olarak filtreleyen, metinlerini temizleyen ve arşivleyen Python tabanlı haber takip aracı.

---

## Özellikler

- **Çoklu Kaynak Tarama:** Webrazzi, Technopat, ShiftDelete, DonanımHaber ve WebTekno RSS akışlarını tek seferde tarar.
- **Akıllı Regex Filtreleme:** Kelime sınırları (`\b`) kullanarak yalnızca yapay zeka, makine öğrenmesi, LLM modelleri ve AI ajanları ile ilgili haberleri yakalar, yanlış eşleşmeleri önler.
- **Otomatik Metin Temizliği:** Haber özetlerindeki HTML etiketlerini, bozuk karakterleri ve *"Devamı..."* / *"İşte detaylar..."* gibi şablon kalıntılarını temizler.
- **Artımlı Arşivleme:** Mevcut `ai_haberleri.csv` dosyasındaki en son haber tarihini kontrol eder; yalnızca yeni yayınlanan haberleri çekip eski arşive ekler ve tekrarlayan linkleri otomatik temizler.
- **Excel Uyumlu Çıktı:** Türkçe karakter sorununu önlemek için `UTF-8-SIG` kodlaması ve `;` ayıracı ile doğrudan Excel'de sorunsuz açılan CSV çıktısı üretir.

---

## Proje Yapısı

```text
ai-trend-radar/
├── rss_analiz.py       # Ana veri çekme, filtreleme ve temizleme betiği
├── ai_haberleri.csv    # Çekilen ve temizlenen haberlerin tutulduğu örnek arşiv dosyası
├── requirements.txt    # Gerekli Python kütüphaneleri
└── README.md           # Proje dokümantasyonu
