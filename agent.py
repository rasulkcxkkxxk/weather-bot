import requests
from bs4 import BeautifulSoup

# === AYARLAR ===
TELEGRAM_TOKEN = "8363632226:AAEutZ0u1Q0axyWCPz4uJwh64V-Tnxeu0o0"
CHAT_ID = "1247237458"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"  # Claude AI yorumu için (opsiyonel)

def get_weather():
    """Google'dan Antalya hava durumunu çeker."""
    url = "https://www.google.com/search?q=antalya+hava+durumu&hl=tr"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    # Sıcaklık
    temp_elem = soup.find("span", {"id": "wob_tm"})
    temp = temp_elem.text.strip() if temp_elem else "?"

    # Hava durumu açıklaması
    desc_elem = soup.find("span", {"id": "wob_dc"})
    desc = desc_elem.text.strip() if desc_elem else "?"

    # Nem
    hum_elem = soup.find("span", {"id": "wob_hm"})
    hum = hum_elem.text.strip() if hum_elem else "?"

    # Rüzgar
    wind_elem = soup.find("span", {"id": "wob_ws"})
    wind = wind_elem.text.strip() if wind_elem else "?"

    return {
        "temp": temp,
        "desc": desc,
        "humidity": hum,
        "wind": wind
    }

def get_ai_comment(weather_data):
    """Claude AI'dan hava yorumu alır."""
    if ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY":
        return "🤖 AI yorum: API anahtarı ayarlanmamış."

    prompt = f"""Antalya'nın şu anki hava durumu: {weather_data['temp']}°C, {weather_data['desc']}, nem: {weather_data['humidity']}, rüzgar: {weather_data['wind']}.
Buna göre tek cümlelik samimi ve pratik bir yorum yaz. Türkçe yaz. Emoji kullan. Örnek: 'Dışarı çıkacaksan hafif bir ceket al, akşam serinleyebilir 🧥'"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-opus-4-5",
                "max_tokens": 150,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        data = response.json()
        return "🤖 " + data["content"][0]["text"].strip()
    except Exception as e:
        return f"🤖 AI yorum alınamadı: {e}"

def emoji_for_weather(desc):
    """Hava durumuna göre emoji seçer."""
    desc_lower = desc.lower()
    if any(w in desc_lower for w in ["güneş", "açık", "clear", "sunny"]):
        return "☀️"
    elif any(w in desc_lower for w in ["bulut", "cloudy", "kapalı"]):
        return "☁️"
    elif any(w in desc_lower for w in ["yağmur", "rain", "yağış"]):
        return "🌧️"
    elif any(w in desc_lower for w in ["fırtına", "storm", "thunder"]):
        return "⛈️"
    elif any(w in desc_lower for w in ["kar", "snow"]):
        return "❄️"
    elif any(w in desc_lower for w in ["sis", "fog", "mist"]):
        return "🌫️"
    else:
        return "🌤️"

def send_telegram(message):
    """Telegram'a mesaj gönderir."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload, timeout=10)
    if r.status_code == 200:
        print("✅ Telegram mesajı gönderildi.")
    else:
        print(f"❌ Telegram hatası: {r.text}")
    return r.status_code == 200

def main():
    print("🌤️ Hava durumu çekiliyor...")

    try:
        w = get_weather()
        emoji = emoji_for_weather(w["desc"])

        # AI yorumu al
        ai_comment = get_ai_comment(w)

        # Mesajı formatla
        message = (
            f"{emoji} <b>Antalya Hava Durumu</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🌡️ <b>Sıcaklık:</b> {w['temp']}°C\n"
            f"🌈 <b>Durum:</b> {w['desc']}\n"
            f"💧 <b>Nem:</b> {w['humidity']}\n"
            f"💨 <b>Rüzgar:</b> {w['wind']}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{ai_comment}"
        )

        print(message)
        send_telegram(message)

    except Exception as e:
        error_msg = f"⚠️ Hava durumu alınamadı: {e}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
