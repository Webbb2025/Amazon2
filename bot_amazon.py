import requests
import os
import time
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# -------------------------------------------
# PARSEAR ARCHIVO amazon.txt
# -------------------------------------------
def leer_productos(filename="amazon.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = [b.strip() for b in contenido.split("\n\n") if b.strip()]
    productos = []

    for bloque in bloques:
        producto = {}
        lineas = bloque.split("\n")

        for linea in lineas:
            if "=" in linea:
                key, valor = linea.split("=", 1)
                key = key.strip()
                valor = valor.strip().strip('"')
                producto[key] = valor

        productos.append(producto)

    return productos


# -------------------------------------------
# ENVIAR PRODUCTO A TELEGRAM
# -------------------------------------------
def send_product_to_telegram(p):
    title = p["TITULO"]
    image_url = p["URL_IMG"]
    price = p["PRECIO"]
    old_price = p["PRECIO_ANT"]
    discount = p["DESCUENTO"]
    url = p["URL_AFI"]

    headers = {"User-Agent": "Mozilla/5.0"}
    img_response = requests.get(image_url, headers=headers)

    if img_response.status_code != 200:
        print("❌ Error descargando imagen:", image_url)
        return

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    message = f"""
<b>{title}</b>

💰 <b>{price}</b>
❌ <b>{old_price}</b>
🔥 <b>{discount}</b>

🔗 {url}
"""

    files = {"photo": ("producto.jpg", img_response.content)}

    data = {
        "chat_id": CHAT_ID,
        "caption": message,
        "parse_mode": "HTML"
    }

    response = requests.post(telegram_url, data=data, files=files)

    if response.status_code == 200:
        print("✅ Enviado:", title[:40])
    else:
        print("❌ Error:", response.status_code, response.text)


# -------------------------------------------
# MAIN
# -------------------------------------------
if __name__ == "__main__":
    productos = leer_productos("amazon.txt")

    if not productos:
        print("⚠ No hay productos en el archivo amazon.txt")
        sys.exit(0)

    for idx, producto in enumerate(productos):
        send_product_to_telegram(producto)

        if idx < len(productos) - 1:
            print("⏳ Esperando 6 minutos antes del siguiente producto...")
            time.sleep(360)

    print("✅ Todos los productos han sido enviados. Finalizando proceso.")
    sys.exit(0)


