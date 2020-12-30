import logging
import configparser as cfg
import os
import random
import sys
from datetime import date
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from scrapper import pemex_scrapper


# Configurar Logging
logging.basicConfig(
    level= logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
)
logger = logging.getLogger()

# Solicitar TOKEN
# Metodo Config FIle:
# def read_token_from_cfg_file(config_file):
#     parser = cfg.ConfigParser()
#     parser.read(config_file)
#     return parser.get('creds','token')
# token = read_token_from_cfg_file('./config.cfg')

# Solicitar TOKEN y MODE
# Metodo Env Variables
TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")

# Revisar MODE de ejecucion
if MODE.lower() == "dev":
    # Accesso Local (desarrollo)
    def run(updater):
        updater.start_polling()
        print('BOT CARGADO')
        updater.idle()
elif MODE.lower() == "prod":
    # Acesso desde Heroku (produccion)
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
else:
    logger.info("NO SE ESPECIFICO EL MODE.")
    sys.exit()


def start(update, context):
    user_id = update.effective_user['id']
    name = update.effective_user['first_name']
    logger.info(f"El usuario ({name} - id:{user_id}), ha iniciado una conversación")
    
    text = f"Bienvenido {name}, yo soy tu un bot 🤖.\nTe puedo ayudar a revisar los concursos de <b>PEMEX.COM</b>.\nPara comenzar escribe:\n/concursos"
    context.bot.sendMessage(chat_id= user_id, parse_mode="HTML", text=text)


def concursos(update, context):
    user_id = update.effective_user['id']
    name = update.effective_user['first_name']
    logger.info(f"El usuario ({name} - id:{user_id}), ha solicitado un información sobre los concursos")
    
    pemex_url = "https://www.pemex.com/procura/procedimientos-de-contratacion/concursosabiertos/Paginas/Pemex-Transformaci%C3%B3n-Industrial.aspx"
    content = pemex_scrapper(pemex_url)

    text = "💡 <b> Concursos "+str(date.today())+"</b> 💡 \n\n"
    for i in content:
        # logger.info(f"Event Data: {i['Publicado']}, {i['Descripción']}")
        e = "🛢️ <b>"+ i['No. Evento'] + "</b>\n<i>"+ i['Publicado'] + '</i>\n\n'
        s = i["Descripción"]+"\n\n ----------------------------------------- \n\n"
        s = s.replace("&quot", "").replace("&nbsp", " ").replace("&apos", "").replace("<br>", ";")
        text = text + e + s
    print(text)
    context.bot.sendMessage(chat_id= user_id, parse_mode="HTML", text=text)


def echo(update, context):
    user_id = update.effective_user['id']
    name = update.effective_user['first_name']
    logger.info(f"El usuario ({name} - id:{user_id}), ha enviado un mensaje")

    text = update.message.text
    context.bot.sendMessage(chat_id=user_id, parse_mode="MarkdownV2", text=f"*Escribiste:*\n_{text}_")


if __name__ == "__main__":

    # Obtenemos informacion
    mybot = telegram.Bot(token = TOKEN)
    print(mybot.getMe())


# Enlasamos nuestr updater con Bot
updater = Updater(mybot.token, use_context = True)

# Creamos un despachador
dp = updater.dispatcher

# Creamos los manejadores
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("concursos", concursos))
dp.add_handler(MessageHandler(Filters.text, echo))

run(updater)