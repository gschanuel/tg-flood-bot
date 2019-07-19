"""
References:
    https://core.telegram.org/bots/api
    https://python-telegram-bot.readthedocs.io/en/latest
"""
import time
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval
from telegram.ext import Updater, MessageHandler, Filters
from random import randint

data = []
switch = []
xinga=["paquita do capeta!", "espantalho do fandangos", "bife de rato", "saco de vacilo", "saco de lixo de peruca", "geladinho de chorume", "bafo de bunda", "metralhadora de bosta", "sofá de zona", "filhote de lombriga", "cara de cu com cãibra", "vai coçar o cu com serrote", "enfia um rojão no cu e sai voando", "você não vale o peido de uma jumenta", "você nasceu pelo cu", "vai chupar um prego até virar tachinha", "vai arrastar o cu na brita", "você come pizza com colher", "arrombado do caralho", "chifrudo", "sua mãe tem pelo no dente", "o padre te benzeu com agua parada", "seu monte de esterco", "seu pai vende carta de magic roubada pra ver site porno na lan house"]
def logger(bot, update):
    #bot.send_message(chat_id=update.message.chat_id, text=msg)
    msg=str(update.message.chat_id)+":"+str(update.message.from_user.id)+":"+str(update.message.message_id)
    print ("[!][logger] " + msg)
    data.append(msg)
    Timer(msg_interval, noflood, [bot, update]).start()

def deleteMsgs(bot, update, msgIDs):
    chat_id=str(update.message.chat_id)
    user_id=str(update.message.from_user.id)
    for msg in msgIDs[msg_flood:]:
        Thread(target=deleteMsg, args=(bot, update, int(msg),),).start()
    msg="[!] Cala a boca " + str(update.message.from_user.first_name) + ", " + str(xinga[randint(0, 23)]) + "!"
    bot.send_message(chat_id,msg)	
        

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
#        msg="[!] Cala a boca " + str(update.message.from_user.first_name) + ", " + str(xinga[randint(0, 23)]) + "!"
#        bot.send_message(chat_id,msg)	
        data.clear()
#        for msg in msgIds[msg_flood:]:
#            Thread(target=deleteMsg, args=(bot, update, int(msg),),).start()
        deleteMsgs(bot, update,msgIds)
    elif counter < msg_flood:
        data.clear()

updater = Updater(token=TOKEN)
dp = updater.dispatcher
flood_handler = MessageHandler(Filters.animation | Filters.photo | Filters.video, logger)
#flood_handler = MessageHandler(Filters.text, logger)
dp.add_handler(flood_handler)
updater.start_polling()
updater.idle()
