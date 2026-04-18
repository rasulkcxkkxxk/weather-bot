import requests

# === AYARLAR ===
TELEGRAM_TOKEN = "8363632226:AAEutZ0u1Q0axyWCPz4uJwh64V-Tnxeu0o0"
CHAT_ID = "1247237458"

# Antalya koordinatları
LAT = 36.8969
LON = 30.7133

def get_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m"
        f"&timezone=Europe/Istanbul"
        f"&windspeed_unit=kmh"
    )
    r = requests.get(url, timeout=10)
    data = r.json()
    current = data["current"]

    temp = round(current["temperature_2m"])
    humidity = current["relative_humidity_2m"]
    wind = round(current["windspeed_10m"])
    code = current["weathercode"]

    desc, emoji = weather_code_to_text(code)
    return {"temp": temp, "humidity": humidity, "wind": wind, "desc": desc, "emoji": emoji}

def weather_code_to_text(code):
    codes = {
        0:  ("Açık ve güneşli",        "☀️"),
        1:  ("Çoğunlukla açık",         "🌤️"),
        2:  ("Parçalı bulutlu",         "⛅"),
        3:  ("Kapalı",                  "☁️"),
        45: ("Sisli",                   "🌫️"),
        48: ("Yoğun sisli",             "🌫️"),
        51: ("Hafif çisenti",           "🌦️"),
        53: ("Orta çisenti",            "🌦️"),
        55: ("Yoğun çisenti",           "🌧️"),
        61: ("Hafif yağmurlu",          "🌧️"),
        63: ("Orta yağmurlu",           "🌧️"),
        65: ("Şiddetli yağmurlu",       "🌧️"),
        71: ("Hafif karlı",             "🌨️"),
        73: ("Orta karlı",              "❄️"),
        75: ("Yoğun karlı",             "❄️"),
        80: ("Hafif sağanak",           "🌦️"),
        81: ("Orta sağanak",            "🌧️"),
        82: ("Şiddetli sağanak",        "⛈️"),
        95: ("Gökgürültülü fırtına",    "⛈️"),
        96: ("Dolu ile fırtına",        "⛈️"),
        99: ("Şiddetli dolu fırtınası", "⛈️"),
    }
    return codes.get(code, ("Bilinmiyor", "🌡️"))

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    r = requests.post(url, json=payload, timeout=10)
    if r.status_code == 200:
        print("✅ Telegram mesajı gönderildi.")
    else:
        print(f"❌ Telegram hatası: {r.text}")

def main():
    print("🌤️ Hava durumu çekiliyor...")
    try:
        w = get_weather()
        message = (
            f"{w['emoji']} <b>Antalya Hava Durumu</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🌡️ <b>Sıcaklık:</b> {w['temp']}°C\n"
            f"🌈 <b>Durum:</b> {w['desc']}\n"
            f"💧 <b>Nem:</b> %{w['humidity']}\n"
            f"💨 <b>Rüzgar:</b> {w['wind']} km/s\n"
            f"━━━━━━━━━━━━━━━━"
        )
        print(message)
        send_telegram(message)
    except Exception as e:
        error_msg = f"⚠️ Hata oluştu: {e}"
        print(error_msg)
        send_telegram(error_msg)

if __name__ == "__main__":
    main()
