import feedparser
import pandas as pd
import re
import csv
import html
from datetime import datetime
import os

# Veri çekmek istediğimiz sitelerin RSS linkleri
rss_kaynaklari = {
    "Webrazzi": "https://webrazzi.com/feed/",
    "Technopat": "https://feedpress.me/technopat",
    "ShiftDelete": "https://shiftdelete.net/feed",
    "DonanimHaber": "https://www.donanimhaber.com/rss/tum/",
    "WebTekno": "https://www.webtekno.com/rss.xml"
    }

# Sadece bu kelimeleri içeren haberler alıncak(ekleme yapılabilir listeye)
anahtar_kelimeler = [
    # Genel terimler
    "yapay zeka", "yapay zekâ", "artificial intelligence", 
    "makine öğrenimi", "makine öğrenmesi", "machine learning",
    "derin öğrenme", "deep learning", "doğal dil işleme", "nlp",
    "büyük dil modeli", "llm", "üretken yapay zeka", "generative ai", "genai","ai","ml","dl",

    # Popüler modeller ve araçlar
    "chatgpt", "gpt-4", "gpt-4o", "gemini", "claude", "copilot",
    "midjourney", "dall-e", "stable diffusion", "sora", "llama",
    "mistral", "deepseek", "grok", "perplexity",

    # Şirketler
    "openai", "anthropic", "hugging face", "deepmind", "xai",

    # Teknik ve ajan odaklı kavramlar
    "rag", "fine-tuning", "yapay zeka ajanı", "ai agent","harness", "agent"
]

# Regex ile kelime sınırlarını belirliyoruz.
# Bu kod, "ai" için \bai\b arar; "tamir"i değil sadece bağımsız "ai" kelimesini bulur.
kelime_kalibi = r'\b(?:' + '|'.join(map(re.escape, anahtar_kelimeler)) + r')\b'
regex_filtresi = re.compile(kelime_kalibi, re.IGNORECASE)

veri_havuzu = []

print("Veriler çekiliyor ve temizleniyor, lütfen bekle...\n")

for kaynak_adi, url in rss_kaynaklari.items():
    feed = feedparser.parse(url)
    
    for haber in feed.entries:
        baslik = html.unescape(haber.get("title", ""))
        ozet = html.unescape(haber.get("summary", ""))
        link = haber.get("link", "")
        tarih = haber.get("published", "")
        try:
            dt = datetime.strptime(tarih, "%a, %d %b %Y %H:%M:%S %z")
            tarih = dt.strftime("%a, %d %b %Y %H:%M")
        except:
            pass
        
        # Başlık ve özeti birleştir
        icerik = baslik + " " + ozet
        
        # Regex ile filtreleme yap
        if regex_filtresi.search(icerik):
            
            # HTML etiketlerini temizle (<p>, <div> vb. sil)
            temiz_ozet = re.sub(r'<[^>]+>', '', ozet)

            # HTML karakterlerini çöz
            temiz_ozet = html.unescape(temiz_ozet)

            # Boşlukları düzelt
            temiz_ozet = re.sub(r'\s+', ' ', temiz_ozet).strip()

            # Şablon kalıntılarını temizle
            temiz_ozet = re.sub(r'\[\.\.\.\]\s*Devamı:.*$', '', temiz_ozet)
            temiz_ozet = re.sub(r'İşte detaylar\.{2,3}$', '', temiz_ozet).strip()

            # Gereksiz boşlukları tek boşluğa düşür
            temiz_ozet = re.sub(r'\s+', ' ', temiz_ozet)
            
            veri_havuzu.append({
                "Kaynak": kaynak_adi,
                "Tarih": tarih,
                "Baslik": baslik,
                "Ozet": temiz_ozet,
                "Link": link
            })

# Listeyi Pandas DataFrame'e çevir
df = pd.DataFrame(veri_havuzu)

# Eğer veri çekildiyse ekrana yazdır
if not df.empty:
    dosya_adi = "ai_haberleri.csv"
    simdi = pd.Timestamp.now(tz='Europe/Istanbul')
    
    # Varsayılan başlangıç tarihi (eğer dosya yoksa ilk çalıştırmada son 1 günü al)
    baslangic_tarihi = simdi - pd.Timedelta(days=1)
    eski_veriler = None
    df['Tarih'] = pd.to_datetime(df['Tarih'], utc=True, errors='coerce')
    df['Tarih'] = df['Tarih'].dt.tz_convert('Europe/Istanbul')

    # 1. Dosya zaten varsa, en son kaydedilen tarihi bul
    if os.path.exists(dosya_adi):
        eski_veriler = pd.read_csv(dosya_adi, sep=";")

        # Eski verilerdeki tarihleri datetime'a çevirip en büyüğünü (en sonuncuyu) al
        gecici_tarihler = pd.to_datetime(eski_veriler['Tarih'], errors='coerce')
        en_son_tarih = gecici_tarihler.max()
        
        if pd.notna(en_son_tarih):
            # En son haberin tarihini Türkiye saatine ayarla
            baslangic_tarihi = en_son_tarih.tz_localize('Europe/Istanbul')
            print(f"Arşivdeki en son haber tarihi: {baslangic_tarihi.strftime('%Y-%m-%d %H:%M')}")
            print("Bu tarihten itibaren yeni haberler aranıyor...")

    # 2. Sadece başlangıç tarihinden (en son haberten) sonraki verileri tut
    df = df[df['Tarih'] >= baslangic_tarihi].copy()
    
    # 3. Tarihi Excel'de çok düzgün görünecek şekilde formatla
    df['Tarih'] = df['Tarih'].dt.strftime('%Y-%m-%d %H:%M')
    
    print(f"Başarılı! Belirtilen tarihten itibaren {len(df)} adet yeni Yapay Zeka haberi bulundu.\n")
    
    # 4. Eski verilerle yeni verileri birleştir
    if eski_veriler is not None:
        df = pd.concat([eski_veriler, df], ignore_index=True)
        
        # Aynı Linke sahip (tekrarlayan) haberleri sil, sadece ilkini tut
        df = df.drop_duplicates(subset=['Link'], keep='first')
        print("Eski verilerle birleştirildi (tekrarlayan haberler temizlendi).")
    
    # Birleştirilmiş veriyi kaydet
    df.to_csv(
        dosya_adi,
        index=False,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL,
        sep=";"
        )
    print(f"\nToplam {len(df)} veri '{dosya_adi}' dosyasına başarıyla kaydedildi!")
else:
    print("Hiçbir haberde anahtar kelimeler bulunamadı veya siteler yanıt vermedi.")
