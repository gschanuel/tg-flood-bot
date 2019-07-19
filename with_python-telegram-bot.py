"""
References:
    https://core.telegram.org/bots/api
    https://python-telegram-bot.readthedocs.io/en/latest
"""
import time
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval
from telegram.ext import Updater, MessageHandler, Filters

data = []

def logger(bot, update):
    #bot.send_message(chat_id=update.message.chat_id, text=msg)
    msg=str(update.message.chat_id)+":"+str(update.message.from_user.id)+":"+str(update.message.message_id)
    print ("[!][logger] " + msg)
    data.append(msg)
    Timer(msg_interval, noflood, [bot, update]).start()

def deleteMsg(bot, update, msgId):
    chat_id=update.message.chat_id
    print ("[!][deleteMsg] Deleting => " + str(msgId))
    bot.delete_message(chat_id=chat_id, message_id=msgId)

def noflood(bot, update):
    chat_id=str(update.message.chat_id)
    user_id=str(update.message.from_user.id)
    counter = 0
    msgIds = []
    for i, item in enumerate(data):
#        print(chat_id+":"+user_id)
        print(item)
        if (chat_id + ":" + user_id) in item:
            msgIds.append((data[i].split(":")[2]))
            counter += 1
    if counter >= msg_flood:
        msg="[!] Cala a boca " + str(update.message.from_user.first_name) + " viado!"
        bot.send_message(chat_id,msg)	
        data.clear()
        for msg in msgIds[msg_flood:]:
            Thread(target=deleteMsg, args=(bot, update, int(msg),),).start()
    elif counter < msg_flood:
        data.clear()

updater = Updater(token=TOKEN)
dp = updater.dispatcher
flood_handler = MessageHandler(Filters.animation | Filters.photo | Filters.video, logger)
#flood_handler = MessageHandler(Filters.text, logger)
dp.add_handler(flood_handler)
updater.start_polling()
updater.idle()
