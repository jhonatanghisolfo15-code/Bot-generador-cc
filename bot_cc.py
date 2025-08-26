import telebot
import random
import requests

TOKEN = "8386328620:AAGSlcOxE_4CSXG532Q4JSJI64_69RnWkk8"
bot = telebot.TeleBot(TOKEN)

# BINs de prueba válidas (para que devuelvan info)
BINS = {
    "visa": ["411111", "400005", "400551"],
    "mastercard": ["510510", "520082", "555555"],
    "amex": ["378282", "371449"]
}

# Funciones Luhn
def verificar_luhn(numero):
    suma = 0
    for i, digito in enumerate(reversed(numero)):
        n = int(digito)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    return suma % 10 == 0

def agregar_digito_luhn(numero):
    suma = 0
    for i, digito in enumerate(reversed(numero)):
        n = int(digito)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    digito_luhn = (10 - (suma % 10)) % 10
    return numero + str(digito_luhn)

# Consultar BIN
def consultar_bin(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        headers = {"Accept-Version": "3"}
        data = requests.get(url, headers=headers).json()
        info = f"🏦 Banco: {data.get('bank', {}).get('name','Desconocido')}\n"
        info += f"🌍 País: {data.get('country', {}).get('name','Desconocido')}\n"
        info += f"💳 Tipo: {data.get('type','Desconocido')}\n"
        info += f"💳 Marca: {data.get('scheme','Desconocido')}"
        return info
    except:
        return f"🏦 Banco: Desconocido\n🌍 País: Desconocido\n💳 Tipo: Desconocido\n💳 Marca: Desconocido"

# Generar tarjeta desde formato
def generar_tarjeta_desde_formato(formato):
    partes = formato.split("|")
    if len(partes) != 4:
        return None, None, None, None, "Formato incorrecto. Usa: 49317300309xxxx|05|2027|rnd"

    numero, mes, anio, cvv = partes

    # Reemplazar 'x' por números aleatorios
    numero_final = ""
    for c in numero:
        if c.lower() == "x":
            numero_final += str(random.randint(0,9))
        else:
            numero_final += c

    # Mes, año y CVV aleatorio si se pone 'rnd'
    if mes.lower() == "rnd":
        mes = str(random.randint(1,12)).zfill(2)
    if anio.lower() == "rnd":
        anio = str(random.randint(25,30))
    if cvv.lower() == "rnd":
        cvv = str(random.randint(100,999))

    # Luhn
    if not verificar_luhn(numero_final):
        numero_final = agregar_digito_luhn(numero_final[:-1])

    return numero_final, mes, anio, cvv, None

# Comando /start
@bot.message_handler(commands=['start'])
def start(message):
    # Sticker mano saludando
    sticker_id = "CAACAgIAAxkBAAEH4aVixpBvZtYOHdVn4AfCj-SX-UHzgQAC6QIAAv5yUUmh6KkI1b2WPx4E"  # Ejemplo sticker, puedes cambiar
    bot.send_sticker(message.chat.id, sticker_id)
    bot.send_message(message.chat.id, "👋 Hola! Para comenzar a usar el bot, escribe /cmds")

# Comando /cmds
@bot.message_handler(commands=['cmds'])
def cmds(message):
    texto = (
        "📜 Comandos del bot:\n"
        "/gen FORMATO -> Genera 10 tarjetas desde el formato dado\n"
        "   Ejemplo: /gen 49317300309xxxx|05|2027|rnd\n"
        "/bin NUMERO -> Muestra información del BIN de un número\n"
    )
    bot.send_message(message.chat.id, texto)

# Comando /gen
@bot.message_handler(commands=['gen'])
def gen(message):
    try:
        _, formato = message.text.split(maxsplit=1)
        tarjetas = []
        for _ in range(10):
            numero, mes, anio, cvv, error = generar_tarjeta_desde_formato(formato)
            if error:
                bot.reply_to(message, error)
                return
            info_bin = consultar_bin(numero[:6])
            tarjeta = f"💳 Número: {numero}\n📅 Exp: {mes}/{anio}\n🔒 CVV: {cvv}\n{info_bin}"
            tarjetas.append(tarjeta)
        bot.send_message(message.chat.id, "\n\n".join(tarjetas))
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error: {str(e)}\nUsa: /gen 49317300309xxxx|05|2027|rnd")

# Comando /bin
@bot.message_handler(commands=['bin'])
def bin_info(message):
    try:
        _, numero = message.text.split()
        info = consultar_bin(numero[:6])
        bot.send_message(message.chat.id, info)
    except:
        bot.reply_to(message, "Usa: /bin NUMERO_TARJETA")

bot.polling()
