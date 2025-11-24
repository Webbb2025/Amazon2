import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_product_to_telegram(title: str, price: str, url: str, image_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    }

    img_response = requests.get(image_url, headers=headers)

    if img_response.status_code != 200:
        print("❌ No se pudo descargar la imagen")
        print("Status:", img_response.status_code)
        return

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    message = f"""
<b>{title}</b>

💲 <b>Precio:</b> {price}

🔗  {url}
"""

    files = {"photo": ("product.jpg", img_response.content)}

    data = {
        "chat_id": CHAT_ID,
        "caption": message,
        "parse_mode": "HTML"
    }

    response = requests.post(telegram_url, data=data, files=files)

    if response.status_code == 200:
        print("✅ Producto enviado correctamente")
    else:
        print(f"❌ Error al enviar: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    send_product_to_telegram(
        title="Zapatillas Nike Running",
        price="$89.99",
        url="https://www.amazon.com/dp/B0C1234567",
        image_url="https://m.media-amazon.com/images/I/71vJxAMM1NL._AC_SX679_.jpg"
    )

