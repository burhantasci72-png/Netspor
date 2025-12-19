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
            'Accept-Charset': 'utf-8'
        }
        
        response = requests.get(SOURCE_URL, headers=headers, timeout=15)
        
        # Siteden gelen verinin karakter kodlamasını UTF-8 olarak zorluyoruz
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        match_divs = soup.find_all('div', class_='mac', option=True)
        
        lines = ["#EXTM3U\n"]
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"# Son Guncelleme: {current_time}\n")

        for div in match_divs:
            stream_id = div['option']
            
            # Takım ve lig bilgilerini çekiyoruz
            takim_div = div.find('div', class_='match-takimlar')
            alt_div = div.find('div', class_='match-alt')
            
            title = takim_div.get_text(strip=True) if takim_div else "Bilinmeyen Mac"
            alt_bilgi = alt_div.get_text(" | ", strip=True) if alt_div else ""
            
            # Yayın linki
            m3u8_link = f"{STREAM_BASE_URL}{stream_id}.m3u8"
            
            # M3U satırını oluştur (Türkçe karakterlerin bozulmaması için title'ı olduğu gibi alıyoruz)
            lines.append(f'#EXTINF:-1, {title} - {alt_bilgi}\n')
            lines.append(f'{m3u8_link}\n')
            
        # Dosyayı "utf-8" kodlamasıyla kaydediyoruz
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        print(f"Liste basariyla guncellendi: {current_time}")
        
    except Exception as e:
        print(f"Hata olustu: {e}")

if __name__ == "__main__":
    get_links()
