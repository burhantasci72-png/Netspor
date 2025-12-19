import requests
from bs4 import BeautifulSoup
import datetime

SOURCE_URL = "https://netspor-amp.xyz/"
STREAM_BASE_URL = "https://andro.6441255.xyz/checklist/"
OUTPUT_FILE = "netspor_iptv.m3u"

def get_links():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(SOURCE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        match_divs = soup.find_all('div', class_='mac', option=True)
        
        lines = ["#EXTM3U\n"]
        # Güncellenme zamanını başlığa ekleyelim
        lines.append(f"# Guncellenme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for div in match_divs:
            stream_id = div['option']
            title = div.find('div', class_='match-takimlar').get_text(strip=True)
            alt_bilgi = div.find('div', class_='match-alt').get_text(" | ", strip=True)
            
            m3u8_link = f"{STREAM_BASE_URL}{stream_id}.m3u8"
            lines.append(f'#EXTINF:-1, {title} ({alt_bilgi})\n')
            lines.append(f'{m3u8_link}\n')
            
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Liste guncellendi.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    get_links()
