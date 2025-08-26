import telebot
import random
import requests

TOKEN = "8386328620:AAGSlcOxE_4CSXG532Q4JSJI64_69RnWkk8"
bot = telebot.TeleBot(TOKEN)

# Función Luhn
def luhn(numero):
    suma = 0
    for i, dig in enumerate(reversed(numero)):
        n = int(dig)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    return suma % 10 == 0

def add_luhn(numero):
    suma = 0
    for i, dig in enumerate(reversed(numero)):
        n = int(dig)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    digito = (10 - (suma % 10)) % 10
    return numero + str(digito)

# Consultar BIN
def consultar_bin(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        headers = {"Accept-Version": "3"}
        data = requests.get(url, headers=headers).json()
        info = f"({data.get('scheme','Desconocido').upper()} {data.get('type','Desconocido').upper()} - {data.get('bank', {}).get('name','Desconocido')} {data.get('country', {}).get('emoji','🌐')})"
        return info
    except:
        return "(Información del BIN no disponible 🌐)"

# Generar tarjeta desde formato
def generar_tarjeta(formato):
    partes = formato.split("|")
    if len(partes) != 4:
        return None, "Formato incorrecto: 4677xxxxxxx|12|2026|rnd"
    numero, mes, anio, cvv = partes

    numero_final = "".join(str(random.randint(0,9)) if c.lower() == "x" else c for c in numero)

    if mes.lower() == "rnd":
        mes = str(random.randint(1,12)).zfill(2)
    if anio.lower() == "rnd":
        anio = str(random.randint(25,30))
    if cvv.lower() == "rnd":
        cvv = str(random.randint(100,999))

    if not luhn(numero_final):
        numero_final = add_luhn(numero_final[:-1])

    return f"{numero_final}|{mes}|{anio}|{cvv}", None

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Hola! Para comenzar a usar el bot, escribe /cmds")

# /cmds
@bot.message_handler(commands=['cmds'])
def cmds(message):
    texto = (
        "📜 Comandos disponibles:\n"
        "/gen FORMATO -> Genera 10 tarjetas desde el formato\n"
        "   Ejemplo: /gen 4677853xxxxxx|12|2026|rnd\n"
        "/bin NUMERO -> Muestra info del BIN de un número"
    )
    bot.send_message(message.chat.id, texto)

# /bin
@bot.message_handler(commands=['bin'])
def bin_info(message):
    try:
        _, numero = message.text.split()
        info = consultar_bin(numero[:6])
        bot.send_message(message.chat.id, f"Bin: {numero[:6]}\nInfo: {info}")
    except:
        bot.reply_to(message, "Usa: /bin NUMERO_TARJETA")

# /gen
@bot.message_handler(commands=['gen'])
def gen(message):
    try:
        _, formato = message.text.split(maxsplit=1)
        # Obtener BIN info
        bin_number = formato.split("|")[0][:6]
        info_bin = consultar_bin(bin_number)

        tarjetas = []
        for _ in range(10):
            tarjeta, error = generar_tarjeta(formato)
            if error:
                bot.reply_to(message, error)
                return
            tarjetas.append(tarjeta)

        resultado = f"🌀 Generador de Tarjetas\n====================\nBin -> {bin_number}\nFormat -> {formato}\nInformation -> {info_bin}\n====================\n" + "\n".join(tarjetas) + "\n===================="
        bot.send_message(message.chat.id, resultado)
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error: {str(e)}\nUsa: /gen FORMATO")
        
bot.polling()
