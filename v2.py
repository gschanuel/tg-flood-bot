"""
References:
    https://core.telegram.org/bots/api
    https://github.com/eternnoir/pyTelegramBotAPI
    https://pypi.org/project/pyTelegramBotAPI
"""

import telebot
import time
from threading import Thread, Timer
from settings import TOKEN, msg_flood, msg_interval

bot = telebot.TeleBot(TOKEN)
"""
'message_id': 131, {
  'from': {
    'id': 419316440,
    'is_bot': False,
    'first_name': 'Gabriel',
    'last_name': 'Schanuel',
    'username': 'GSchanuel',
    'language_code': 'pt-br'
    },
  'chat': {
    'id': -1001215799687,
    'title': 'Teste_bot',
    'type': 'supergroup'
  },
  'date': 1563480155,
  'text': '2'
}
"""


data = []


def deleteMsg(chat_id, msgId):
    bot.delete_message(chat_id,msgId)

def noflood(user_id, chat_id):
    counter = 0
    msgIds = []
    for i, item in enumerate(data):
        if (chat_id+":"+user_id) in item:
            msgIds.append((data[i].split(":")[2]))
            counter += 1
    if counter >= msg_flood:
        print ("[!] identificado")
        #bot.send_message(chat_id,"identificado")	
        data.clear()
        for msg in msgIds[msg_flood:]:
            Thread(target=deleteMsg, args=(chat_id, int(msg),),).start()
    elif counter < msg_flood:
        data.clear()

#@bot.message_handler(content_types=['photo', 'sticker', 'video'])
@bot.message_handler(func=lambda message: True)
def handle_gifs(message):
    print ("[!] " + str(message.chat.id) + ": " + str(message.message_id))
    data.append(str(message.chat.id)+":"+str(message.from_user.id)+":"+str(message.message_id))
    Timer(msg_interval, noflood, [str(message.from_user.id), str(message.chat.id)]).start()

bot.polling()
