import requests
import os
import time
import sys
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LOG_FILE = "enviados.log"
TIMESTAMP_FILE = "log_timestamp.txt"

# -------------------------------------------
# CONTROL DEL RESETEO AUTOMÁTICO DEL LOG
# -------------------------------------------
def resetear_log_si_corresponde():
    """Reinicia el log si han pasado 14 días."""
    if not os.path.exists(TIMESTAMP_FILE):  
        # Primera ejecución → crear timestamp
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(datetime.now().isoformat())
        return

    try:
        with open(TIMESTAMP_FILE, "r") as f:
            fecha_str = f.read().strip()
            ultima_fecha = datetime.fromisoformat(fecha_str)
    except:
        # Si hay un error, reiniciar timestamp
        ultima_fecha = datetime.now()
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(ultima_fecha.isoformat())

    # Si pasaron 14 días → resetear
    if datetime.now() - ultima_fecha >= timedelta(days=14):
        print("🗑 Reseteando enviados.log (han pasado 14 días)")
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

        # Actualizar fecha del timestamp
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(datetime.now().isoformat())

# -------------------------------------------
# LEER LOG DE PRODUCTOS YA ENVIADOS
# -------------------------------------------
def cargar_enviados():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def guardar_enviado(asin):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(asin + "\n")

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
                producto[key.strip()] = valor.strip().strip('"')
        productos.append(producto)

    return productos

# -------------------------------------------
# ENVIAR PRODUCTO A TELEGRAM
# -------------------------------------------
def send_product_to_telegram(p):
    title = p["TITULO"]
    asin = p["ASIN"]
    image_url = p["URL_IMG"]
    price = p["PRECIO"]
    old_price = p["PRECIO_ANT"]
    discount = p["DESCUENTO"]
    url = p["URL_AFI"]

    headers = {"User-Agent": "Mozilla/5.0"}
    img_response = requests.get(image_url, headers=headers)

    if img_response.status_code != 200:
        print("❌ Error descargando imagen:", image_url)
        return False

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    message = f"""
<b>{title}</b>

💰 <b>{price}</b>
❌ <b>{old_price}</b>
🔥 <b>{discount}</b>

🔗 {url}
"""

    files = {"photo": ("producto.jpg", img_response.content)}
    data = {"chat_id": CHAT_ID, "caption": message, "parse_mode": "HTML"}

    response = requests.post(telegram_url, data=data, files=files)

    if response.status_code == 200:
        print("✅ Enviado:", title[:40])
        guardar_enviado(asin)
        return True
    else:
        print("❌ Error:", response.status_code, response.text)
        return False

# -------------------------------------------
# MAIN
# -------------------------------------------
if __name__ == "__main__":

    # 1️⃣ Resetear log si tocaba
    resetear_log_si_corresponde()

    # 2️⃣ Cargar log existente
    enviados = cargar_enviados()

    # 3️⃣ Leer productos
    productos = leer_productos("amazon.txt")

    if not productos:
        print("⚠ No hay productos en el archivo amazon.txt")
        sys.exit(0)

    for idx, producto in enumerate(productos):

        asin = producto.get("ASIN")

        if asin in enviados:
            print(f"⏭ Saltando (ya enviado): {asin}")
            continue

        enviado = send_product_to_telegram(producto)

        if not enviado:
            print("⚠ Falló el envío, continuando con el siguiente.")
        
        if idx < len(productos) - 1:
            print("⏳ Esperando 6 minutos antes del siguiente producto...")
            time.sleep(600)

    print("✅ Todos los productos procesados.")
    sys.exit(0)
