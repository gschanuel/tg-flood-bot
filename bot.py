"""
References:
    https://core.telegram.org/bots/api
    https://python-telegram-bot.readthedocs.io/en/latest
"""
import datetime
import time
import telegram 
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval, botName 
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from sys import exit
from db_handler import MySQL_DB
import random

import logging
from systemd.journal import JournaldLogHandler

db = MySQL_DB()

logger = logging.getLogger(botName)
journald_handler = JournaldLogHandler()

journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

logger.addHandler(journald_handler)

logger.setLevel(logging.DEBUG)


flood_counter = []
data = []

flood_data={}

def on_new_animation(bot, update):
    logger.info("[!][on_new_animation]")
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    msg_id = update.message.id

    try:
        item = "{}:{}:{}".format(chat_id, user_id, msg_id)
        logger.info("[!][New Animation] {}".format(item))
    
        data.append(item)
        flood_counter.append(item)
        
        flood_data[chat_id][user_id].append(msg_id)
    
        check_flood(bot, update)
        Timer(msg_interval, timeout, [bot, update]).start()
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def deleteMsgs(bot, update, msgIDs):
    logger.info("[!][deleteMsgs]")
    try:
        chat_id = str(update.message.chat_id)
        user_id = str(update.message.from_user.id)
        for msg in msgIDs[msg_flood:]:
            Thread(target=deleteMsg, args=(bot, update, int(msg),),).start()
            item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, msg)
            data.remove(item)
        xinga(bot, update)
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def xinga(bot, update):
    logger.info("[!][xinga]")
    try:
        query = "SELECT text FROM xingamento ORDER BY RAND() LIMIT 1"
        db.cursor.execute(query)
        row = db.cursor.fetchone()
        quote = "__{}__".format(row[0])

        msg = "[!] Cala a boca {}, {}!".format(update.message.from_user.first_name, quote)
        bot.send_message(update.message.chat_id, msg, parse_mode='Markdown')
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def deleteMsg(bot, update, msgId):
    logger.info("[!][deleteMsg]")
    try:
        chat_id = update.message.chat_id
        logger.info("[!][deleteMsg] Deleting = > {}".format(msgId))
    
        bot.delete_message(chat_id=chat_id, message_id=msgId)
        item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, msgId)
        data.remove(item)
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def check_flood(bot, update):
    logger.info("[!][check_flood]")
    try:
        chat_id = str(update.message.chat_id)
        user_id = str(update.message.from_user.id)
        counter = 0
        # msgIds = []

        logger.info("[!] Checking flood")

        for i, item in enumerate(flood_counter):
            if (chat_id + ":" + user_id) in item:
                # msgIds.append((flood_counter[i].split(":")[2]))
                counter += 1
        if counter > msg_flood:
            logger.info("[!] Flood in action: {} ({})".format(user_id, counter))
            # Thread(target = deleteMsg, args = (bot, update, update.message.message_id), ).start()
            deleteMsg(bot, update, update.message.message_id)
            # deleteMsgs(bot, update, msgIds)
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def timeout(bot, update):
    logger.info("[!][timeout]")
    try:
        logger.info("[!] timeout - flood_counter: {}".format(flood_counter))
        logger.info("[!] timeout - data: {}".format(data))
        item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, update.message.message_id)
        flood_counter.remove(item)
        # data.remove(item)
    except Exception as e:
        loggaer.info(str(e))


def logging(bot, update):
    try:
        photo = ""
        query = ("INSERT INTO log (message_id, date, chat_id, text, photo, from_id, first_name, last_name, username) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')").format(update.message.message_id, str(update.message.date), update.message.chat.id, str(update.message.text), photo, update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username)
# else:
#     photo = update.message.photo.file_id
#logger.info(photo) 
#     logger.info(query)
        db.cursor.execute(query)
        db.con.commit()
        logger.info("{}:{}:{}".format(update.message.chat.id, update.message.from_user.first_name, update.message.text))
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def put_quote(bot, update):
    logger.info("[!][put_quote]")
    try:
        message_id = update.message.reply_to_message.message_id
        query = ("INSERT INTO quote (message_id, chat_id) VALUES ('{}', '{}')").format(message_id, update.message.chat_id)
        db.cursor.execute(query)
        db.con.commit()
        logger.info("{} - OK".format(db.cursor.lastrowid))
        bot.send_message(update.message.chat.id, "Salvei \"{}\" com id {}".format(update.message.reply_to_message.text, db.cursor.lastrowid))
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


def get_quote(bot, update):
    logger.info("[!][get_quote]")
    print("[!][get_quote]")
    try:
        if update.message.text == "/lauters":
            query = "SELECT text FROM lauters ORDER BY RAND() LIMIT 1"
        else:
            quote_id = (update.message.text).split(" ")
            if len(quote_id) > 1:
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} AND id = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id, int(quote_id[1]))
            else:
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id)
    
            db.cursor.execute(query)
            message_id = db.cursor.fetchone()[0]
            query = "SELECT text FROM log WHERE message_id = {}".format(message_id)
#        logger.info(query)
        db.cursor.execute(query)
        row = db.cursor.fetchone()
        quote = "__{}__".format(row[0])
#        logger.info(quote) 

        bot.send_message(update.message.chat_id, quote, parse_mode='Markdown')

    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)
#    logger.info(row)

def list_quotes(bot, update):
    print("[!] list_quotes")
    quotes_list = ""
    try:
        query = "SELECT quote.id, log.text FROM quote, log WHERE quote.chat_id = {} AND quote.message_id=log.message_id".format(update.message.chat_id)
        db.cursor.execute(query)
        results = db.cursor.fetchall()
        for result in results:
            quotes_list += "#{}: {} \n".format(result[0], result[1])
        bot.send_message(update.message.from_user.id, quotes_list)
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)

def call_bot(bot, update):
    logger.info("[!] call_bot")
    try:
        msg = ("Quer falar em particular comigo?\n")
    
        start_bot_keyboard = [[telegram.InlineKeyboardButton(text='Siiiiiiiim, seu lindo!', url="https://t.me/{}?start=payload".format(botName))]]
        
        reply_kb_markup = telegram.InlineKeyboardMarkup(start_bot_keyboard, resize_keyboard=True, one_time_keyboard=True)
    
        bot.send_message(update.message.chat_id, msg, reply_markup=reply_kb_markup) 
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)
    

def start_bot(bot, update):
    try:
        msg = ("Aqui está a lista de comandos que você pode usar no grupo:\n")
        msg += ("/save: Responder uma mensagem com **/save** vai salva-la\n")
        msg += ("/help: Pra iniciar essa conversa (e eu poder falar em particular com você)\n")
        msg += ("/quote: Vai trazer uma frase aleatória que foi salva anteriormente\n")
        msg += ("/quote X: Vai trazer a frase número X\n")
        msg += ("/lauters: Traz uma frase do Lawto\n")
        msg += ("/list: Mostro pra você todas as frases salvas e seus respectivos números")
        bot.send_message(update.message.from_user.id, msg, parse_mode='Markdown')
    except Exception as e:
        logger.exception(str(e))
        sys.exit(1)


try:
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher
    
    log_handler = MessageHandler(Filters.all, logging)
    flood_handler = MessageHandler(Filters.animation | Filters.photo | Filters.video, on_new_animation)
    save_handler = CommandHandler("save", put_quote)
    start_handler = CommandHandler("start", start_bot)
    callbot_handler = CommandHandler("help", call_bot)
    quote_handler = CommandHandler("quote", get_quote)
    lauters_handler = CommandHandler("lauters", get_quote)
    list_quotes_handler = CommandHandler("list", list_quotes)

    dp.add_handler(list_quotes_handler)
    dp.add_handler(save_handler)
    dp.add_handler(start_handler)
    dp.add_handler(callbot_handler)
    dp.add_handler(quote_handler)
    dp.add_handler(lauters_handler)
    dp.add_handler(flood_handler)
    dp.add_handler(log_handler)

    updater.start_polling()
    updater.idle()
except Exception as e:
    logger.exception(str(e))
    sys.exit(1)
