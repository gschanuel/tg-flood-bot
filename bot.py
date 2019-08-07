"""
References:
    https://core.telegram.org/bots/api
    https://python-telegram-bot.readthedocs.io/en/latest
"""
import datetime
import time
# import telegram 
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval, con, cursor
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random

import logging
from systemd.journal import JournaldLogHandler

logger = logging.getLogger(__name__)
journald_handler = JournaldLogHandler()

journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

logger.addHandler(journald_handler)

logger.setLevel(logging.DEBUG)



flood_counter = []
data = []


def on_new_animation(bot, update):
    logger.info("[!][on_new_animation]")
    try:
        item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, update.message.message_id)
        logger.info("[!][New Animation] {}".format(item))
    
        data.append(item)
        flood_counter.append(item)
    
        check_flood(bot, update)
        Timer(msg_interval, timeout, [bot, update]).start()
    except Exception as e:
        logger.info(str(e))


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
        logger.info(str(e))


def xinga(bot, update):
    logger.info("[!][xinga]")
    try:
        query = "SELECT text FROM xingamento ORDER BY RAND() LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        quote = "__{}__".format(row[0])

        msg = "[!] Cala a boca {}, {}!".format(update.message.from_user.first_name, quote)
        bot.send_message(update.message.chat_id, msg, parse_mode='Markdown')
    except Exception as e:
        logger.info(str(e))


def deleteMsg(bot, update, msgId):
    logger.info("[!][deleteMsg]")
    try:
        chat_id = update.message.chat_id
        logger.info("[!][deleteMsg] Deleting = > {}".format(msgId))
    
        bot.delete_message(chat_id=chat_id, message_id=msgId)
        item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, msgId)
        data.remove(item)
    except Exception as e:
        logger.info(str(e))


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
                counter+= 1
        if counter > msg_flood:
            logger.info("[!] Flood in action: {} ({})".format(user_id, counter))
            # Thread(target = deleteMsg, args = (bot, update, update.message.message_id), ).start()
            deleteMsg(bot, update, update.message.message_id)
            # deleteMsgs(bot, update, msgIds)
    except Exception as e:
        logger.info(str(e))


def timeout(bot, update):
    logger.info("[!][timeout]")
    try:
        # logger.info("[!] timeout - flood_counter: {}".format(flood_counter))
        # logger.info("[!] timeout - data: {}".format(data))
        item = "{}:{}:{}".format(update.message.chat_id, update.message.from_user.id, update.message.message_id)
        flood_counter.remove(item)
        # data.remove(item)
    except Exception as e:
        logger.info(str(e))


def logging(bot, update):
    logger.info("[!][logging]")
    logger.info("# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ")
    logger.info(str(update))
    logger.info(" ")
    try:
        photo = ""
        query = ("INSERT INTO log (message_id, date, chat_id, text, photo, from_id, first_name, last_name, username) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')").format(update.message.message_id, str(update.message.date), update.message.chat.id, str(update.message.text), photo, update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username)
# else:
#     photo = update.message.photo.file_id
# logger.info(photo)
#     logger.info(query)
        cursor.execute(query)
        con.commit()
    except Exception as e:
        logger.info(str(e))


def put_quote(bot, update):
    logger.info("[!][put_quote]")
    try:
        message_id = update.message.reply_to_message.message_id
        logger.info(message_id)
        query = ("INSERT INTO quote (message_id, chat_id) VALUES ({}, {})").format(message_id, update.message.chat_id)
        cursor.execute(query)
        con.commit()
        logger.info("OK")
    except Exception as e:
        logger.info(str(e))


def get_quote(bot, update):
    logger.info("[!][get_quote]")
    try:
        if update.message.text == "/lauters":
            query = "SELECT text FROM lauters ORDER BY RAND() LIMIT 1"
        else:
            quote_id = (update.message.text).split(" ")
            if len(quote_id) > 1:
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} AND id = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id, int(quote_id[1]))
            else:
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id)
    
            cursor.execute(query)
            message_id = cursor.fetchone()[0]
            query = "SELECT text FROM log WHERE message_id = {}".format(message_id)
#        logger.info(query)
        cursor.execute(query)
        row = cursor.fetchone()
        quote = "__{}__".format(row[0])
        logger.info(quote) 
    except Exception as e:
        logger.info(str(e))
    logger.info(row)
    bot.send_message(update.message.chat_id, quote, parse_mode='Markdown')


try:
    updater = Updater(token=TOKEN)
    dp = updater.dispatcher
    
    log_handler = MessageHandler(Filters.all, logging)
    flood_handler = MessageHandler(Filters.animation | Filters.photo | Filters.video, on_new_animation)
    save_handler = CommandHandler("save", put_quote)
    quote_handler = CommandHandler("quote", get_quote)
    lauters_handler = CommandHandler("lauters", get_quote)
    
    dp.add_handler(save_handler)
    dp.add_handler(quote_handler)
    dp.add_handler(lauters_handler)
    dp.add_handler(flood_handler)
    dp.add_handler(log_handler)
    
    updater.start_polling()
    updater.idle()
except Exception as e:
    logger.info(str(e))
