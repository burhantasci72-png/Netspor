import requests
from bs4 import BeautifulSoup
import datetime

SOURCE_URL = "https://netspor-amp.xyz/"
STREAM_BASE_URL = "https://andro.6441255.xyz/checklist/"
OUTPUT_FILE = "netspor_iptv.m3u"

def get_links():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(SOURCE_URL, headers=headers, timeout=15)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        lines = ["#EXTM3U\n"]
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"# Son Guncelleme: {current_time}\n")

        # --- 1. KATEGORİ: CANLI TV KANALLARI (BEIN SPORTS VB.) ---
        channels_container = soup.find('div', id='yayinlarKanallar')
        if channels_container:
            channel_items = channels_container.find_all('div', class_='mac', option=True)
            for div in channel_items:
                stream_id = div['option']
                title = div.find('div', class_='match-takimlar').get_text(strip=True)
                # Kategori etiketini group-title olarak ekliyoruz
                m3u8_link = f"{STREAM_BASE_URL}{stream_id}.m3u8"
                lines.append(f'#EXTINF:-1 group-title="CANLI TV KANALLARI", {title}\n')
                lines.append(f'{m3u8_link}\n')

        # --- 2. KATEGORİ: GÜNÜN MAÇLARI ---
        matches_container = soup.find('div', id='yayinlar')
        if matches_container:
            match_items = matches_container.find_all('div', class_='mac', option=True)
            for div in match_items:
                stream_id = div['option']
                
                takim_div = div.find('div', class_='match-takimlar')
                alt_div = div.find('div', class_='match-alt')
                
                title = takim_div.get_text(strip=True) if takim_div else "Bilinmeyen Mac"
                # Eğer maçın yanında CANLI yazısı varsa onu da başlığa ekleyelim
                canli_badge = div.find('div', class_='canli-badge')
                status = "[CANLI] " if canli_badge else ""
                
                alt_bilgi = alt_div.get_text(" | ", strip=True) if alt_div else ""
                
                m3u8_link = f"{STREAM_BASE_URL}{stream_id}.m3u8"
                lines.append(f'#EXTINF:-1 group-title="GUNUN MACLARI", {status}{title} ({alt_bilgi})\n')
                lines.append(f'{m3u8_link}\n')

        # Dosyayı kaydet
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        print(f"Liste 2 kategorili olarak guncellendi: {current_time}")
        
    except Exception as e:
        print(f"Hata olustu: {e}")

if __name__ == "__main__":
    get_links()
