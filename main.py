import requests
import re
import datetime
from bs4 import BeautifulSoup

# --- GENEL AYARLAR ---
OUTPUT_FILE = "Canli_Spor_Hepsi.m3u"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# --- 1. NETSPOR: ÖZEL BEIN 1 GÜNCELLEMELİ ---
def fetch_netspor():
    print("[*] Netspor taranıyor...")
    results = []
    source_url = "https://netspor-amp.xyz/"
    # Yeni domain bilgisini buraya işledik
    stream_base = "https://andro.adece12.sbs/checklist/" 
    
    try:
        res = requests.get(source_url, headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Kanallar ve Maçlar tek bir mantıkla taranıyor
        for div in soup.find_all('div', class_='mac', option=True):
            sid = div.get('option')
            title_div = div.find('div', class_='match-takimlar')
            if not title_div: continue
            
            title = title_div.get_text(strip=True)
            
            # Kategori Belirleme
            if div.find_parent('div', id='kontrolPanelKanallar'):
                group = "CANLI TV KANALLARI"
            else:
                group = "Günün Maçları"
                alt = div.find('div', class_='match-alt')
                if alt: title = f"{title} ({alt.get_text(' | ', strip=True)})"

            # --- ÖZEL LINK KONTROLÜ (beIN Sports 1 için) ---
            if sid == "androstreamlivebs1":
                # Senin verdiğin özel link: receptestt.m3u8
                final_url = f"{stream_base}receptestt.m3u8"
            else:
                # Diğerleri normal ID ile devam eder
                final_url = f"{stream_base}{sid}.m3u8"
            
            results.append({
                "name": title, 
                "url": final_url, 
                "group": group, 
                "ref": source_url, 
                "logo": ""
            })
    except Exception as e:
        print(f"Netspor Hatası: {e}")
    return results

# --- 2. TRGOALS: TÜM KANALLAR ---
def fetch_trgoals():
    print("[*] Trgoals taranıyor...")
    results = []
    domain = None
    for i in range(1485, 2150):
        test = f"https://trgoals{i}.xyz"
        try:
            if requests.head(test, timeout=1).status_code == 200:
                domain = test; break
        except: continue
    
    if domain:
        trg_channels = {
            "yayin1":"BEIN SPORTS 1","yayinb2":"BEIN SPORTS 2","yayinb3":"BEIN SPORTS 3",
            "yayinb4":"BEIN SPORTS 4","yayinb5":"BEIN SPORTS 5","yayinbm1":"BEIN SPORTS MAX 1",
            "yayinbm2":"BEIN SPORTS MAX 2","yayinss":"S SPORT 1","yayinss2":"S SPORT 2",
            "yayint1":"TIVIBU SPOR 1","yayint2":"TIVIBU SPOR 2","yayint3":"TIVIBU SPOR 3",
            "yayint4":"TIVIBU SPOR 4","yayinsmarts":"SMART SPOR 1","yayinsms2":"SMART SPOR 2",
            "yayintrtspor":"TRT SPOR","yayinas":"A SPOR","yayintv8":"TV8","yayintv85":"TV8,5",
            "yayinex1":"TABII 1","yayinex2":"TABII 2"
        }
        for cid, name in trg_channels.items():
            try:
                r = requests.get(f"{domain}/channel.html?id={cid}", headers=HEADERS, timeout=5)
                m = re.search(r'const baseurl = "(.*?)"', r.text)
                if m:
                    results.append({
                        "name": f"TRG - {name}", "url": f"{m.group(1)}{cid}.m3u8",
                        "group": "TRGOALS TV", "ref": f"{domain}/", "logo": "https://i.ibb.co/gFyFDdDN/trgoals.jpg"
                    })
            except: continue
    return results

# --- 3. SELÇUKSPOR: TÜM KANALLAR ---
def fetch_selcuk_sporcafe():
    print("[*] Selçukspor / Sporcafe taranıyor...")
    results = []
    selcuk_list = [
        {"id": "selcukbeinsports1", "n": "BEIN SPORTS 1"}, {"id": "selcukbeinsports2", "n": "BEIN SPORTS 2"},
        {"id": "selcukbeinsports3", "n": "BEIN SPORTS 3"}, {"id": "selcukbeinsports4", "n": "BEIN SPORTS 4"},
        {"id": "selcukbeinsports5", "n": "BEIN SPORTS 5"}, {"id": "selcukssport", "n": "S SPORT 1"},
        {"id": "selcuktivibuspor1", "n": "TIVIBU SPOR 1"}, {"id": "selcuksmartspor", "n": "SMART SPOR 1"}
    ]
    
    referer, html_content = None, None
    for i in range(6, 150):
        url = f"https://www.sporcafe{i}.xyz/"
        try:
            res = requests.get(url, headers=HEADERS, timeout=1)
            if "uxsyplayer" in res.text:
                referer, html_content = url, res.text; break
        except: continue
    
    if html_content and referer:
        m_domain = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html_content)
        if m_domain:
            s_domain = f"https://{m_domain.group(1)}"
            for ch in selcuk_list:
                try:
                    r = requests.get(f"{s_domain}/index.php?id={ch['id']}", headers={**HEADERS, "Referer": referer}, timeout=5)
                    base = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', r.text)
                    if base:
                        results.append({
                            "name": f"SL - {ch['n']}", "url": f"{base.group(1)}{ch['id']}/playlist.m3u8",
                            "group": "SELÇUKSPOR HD", "ref": referer, "logo": ""
                        })
                except: continue
    return results

# --- ANA ÇALIŞTIRICI ---
def main():
    all_streams = []
    all_streams.extend(fetch_netspor())
    all_streams.extend(fetch_trgoals())
    all_streams.extend(fetch_selcuk_sporcafe())
    
    if not all_streams:
        print("Hata: Veri bulunamadı!")
        return

    # Dosyayı Oluştur (UTF-8-SIG Türkçe karakterler için)
    content = "#EXTM3U\n"
    content += f"# Son Guncelleme: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
    for s in all_streams:
        logo = f' tvg-logo="{s["logo"]}"' if s["logo"] else ""
        content += f'#EXTINF:-1 group-title="{s["group"]}"{logo},{s["name"]}\n'
        content += f'#EXTVLCOPT:http-referrer={s["ref"]}\n'
        content += f'{s["url"]}\n'

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as f:
        f.write(content)
    print(f"\n[OK] beIN Sports 1 linki ve tüm kanallar güncellendi.")

if __name__ == "__main__":
    main()
