import os
import requests

# =========================
# Configuración desde entorno
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Verificar que estén definidas
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Debes definir BOT_TOKEN y CHAT_ID en las variables de entorno")

# =========================
# Función para enviar foto
# =========================
def send_to_telegram(message: str, image_url: str = None):
    """
    Envía un mensaje y opcionalmente una foto a Telegram.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    data = {
        "chat_id": CHAT_ID,
        "caption": message
    }
    
    if image_url:
        data["photo"] = image_url
    else:
        # Si no hay imagen, enviamos solo texto
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message
        }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ Mensaje enviado correctamente")
    else:
        print(f"❌ Error al enviar mensaje: {response.status_code}")
        print(response.text)

# =========================
# Ejemplo de uso
# =========================
if __name__ == "__main__":
    mensaje = "¡Hola! Este es un mensaje de prueba desde mi bot."
    imagen = "https://example.com/imagen.jpg"  # Reemplaza con la URL de tu imagen
    send_to_telegram(mensaje, imagen)
