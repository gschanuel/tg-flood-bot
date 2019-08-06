"""
References:
    https://core.telegram.org/bots/api
    https://python-telegram-bot.readthedocs.io/en/latest
"""
import datetime, time, telegram 
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval, con, cursor
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random

data = []
def logger(bot, update):
    msg=str(update.message.chat_id)+":"+str(update.message.from_user.id)+":"+str(update.message.message_id)
    print ("[!][logger] " + msg)
    data.append(msg)
    noflood(bot, update)
    Timer(msg_interval, timeout, [bot, update]).start()

def deleteMsgs(bot, update, msgIDs):
    chat_id=str(update.message.chat_id)
    user_id=str(update.message.from_user.id)
    for msg in msgIDs[msg_flood:]:
        Thread(target=deleteMsg, args=(bot, update, int(msg),),).start()
    xinga(bot, update)

def xinga(bot, update):
    query = "SELECT text FROM xingamento ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    quote = "__{}__".format(row[0])

    msg="[!] Cala a boca {}, {}!".format(update.message.from_user.first_name, quote)
    bot.send_message(chat_id,msg)

def deleteMsg(bot, update, msgId):
    chat_id=update.message.chat_id
    print ("[!][deleteMsg] Deleting => " + str(msgId))
    bot.delete_message(chat_id=chat_id, message_id=msgId)
    xinga(bot, update)

def noflood(bot, update):
    chat_id=str(update.message.chat_id)
    user_id=str(update.message.from_user.id)
    counter = 0
    msgIds = []
    print ("[!] NoFlood check")
    for i, item in enumerate(data):
        if (chat_id + ":" + user_id) in item:
            msgIds.append((data[i].split(":")[2]))
            counter += 1
    if counter >= msg_flood:
        print ("[!] NoFlood action")
        deleteMsg(bot, update, update.message.message_id)

def timeout(bot, update):
    print ("[!] timeout - {}".format(str(data)))
    msg=str(update.message.chat_id)+":"+str(update.message.from_user.id)+":"+str(update.message.message_id)
    data.remove(msg)

def check_flood(bot, update):
    try:
        chat_id=str(update.message.chat_id)
        user_id=str(update.message.from_user.id)
        msg_id=str(update.message.message_id)
        counter = 0
        msgIds = []

        #for i, item in data_limit:
        for i, item in enumerate(data):
            #print ("i = {}; item = {}".format(i,item))
            if (chat_id + ":" + user_id) in item:
                msgIds.append((data[i].split(":")[2]))
                counter += 1
        if counter >= msg_flood:
            deleteMsgs(bot, update, msgIds[msg_flood:])
            msg="[!] Cala a boca " + str(update.message.from_user.first_name) + ", " + str(random.choice(xinga)) + "!"
            bot.send_message(chat_id,msg)
            for msg, msg_item in enumerate(msgIds):
                for i, item in enumerate(data):
                    if (chat_id + ":" + user_id + ":" + str(msg)) in item:
                        #data.remove(item)
                        break
    except Exception as e:
        print (str(e))

#

#def media_type(bot, update):
#    return {
#        'audio': 'ogg'
#        'document': 'pdf'
#        'photo': 'jpg'
#        'sticker': 'gif'
#        'video': 'mp4'
#        'video_note': 'mp4'
#        'voice': 'ogg'
#        }.get 


def logging(bot, update):
#    try:
#    text = update.message.text
#    chat = update.message.chat_id
##   bot.send_message(chat,str(update))
#    print (update.message.message_id)
#    print (update.message.date)
#    print (update.message.chat.id)
#    print (update.message.text)
##    file_id=update.message.photo[-1]
##    newFile = bot.get_file(file_id)
##    newFile.download('meeseks.jpg')
##    print (file_id)
#    print (update.message.from_user.id)
#    print (update.message.from_user.first_name)
#    print (update.message.from_user.last_name)
#    print (update.message.from_user.username)
    print ("##############################")
    print (str(update))
    print (" ")
    try:
        photo = ""
        query =("INSERT INTO log (message_id, date, chat_id, text, photo, from_id, first_name, last_name, username) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')").format(update.message.message_id, str(update.message.date), update.message.chat.id, str(update.message.text), photo, update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username )
#    else:
#        photo = update.message.photo.file_id
#    print(photo)
        print(query)
        cursor.execute(query)
        con.commit()
    except Exception as e:
        print (str(e))
#    cursor.close()
#def get_quote:

def put_quote(bot, update):
    message_id=update.message.reply_to_message.message_id
    print (message_id)
    query=("INSERT INTO quote (message_id, chat_id) VALUES ({}, {})").format(message_id, update.message.chat_id)
    try:
      cursor.execute(query)
      con.commit()
      print ("OK")
    except Exception as e:
        print (str(e))

def get_quote(bot, update):
    print(str(update))
    try:

        if update.message.text == "/lauters":
            query = "SELECT text FROM lauters ORDER BY RAND() LIMIT 1"
        else:
            quote_id=(update.message.text).split(" ")
            if len(quote_id) > 1 :
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} AND id = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id,int(quote_id[1]))
            else:
                query = "SELECT message_ID FROM quote WHERE chat_ID = {} ORDER BY RAND() LIMIT 1".format(update.message.chat_id)
    
            cursor.execute(query)
            message_id=cursor.fetchone()[0]
            query = "SELECT text FROM log WHERE message_id = {}".format(message_id)
#        print (query)
        cursor.execute(query)
        row = cursor.fetchone()
        quote = "__{}__".format(row[0])
        print (quote) 
    except Exception as e:
        print (str(e))
    print(row)
    bot.send_message(update.message.chat_id, quote, parse_mode='Markdown')

updater = Updater(token=TOKEN)
dp = updater.dispatcher


log_handler = MessageHandler(Filters.all, logging)
flood_handler = MessageHandler(Filters.animation | Filters.photo | Filters.video, logger)
dp.add_handler(CommandHandler("save", put_quote))
dp.add_handler(CommandHandler("quote", get_quote))
dp.add_handler(CommandHandler("lauters", get_quote))
dp.add_handler(flood_handler)
dp.add_handler(log_handler)
updater.start_polling()
updater.idle()

