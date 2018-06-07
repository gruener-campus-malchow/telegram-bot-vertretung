import logging
import json
import requests
import sqlite3
from telegram import (ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

# Bot-Token hier einfügen
token = ""

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KLASSE = range(1)

db = sqlite3.connect('gvtbotdata.db', check_same_thread=False)
c = db.cursor()
c.execute(
    '''CREATE TABLE IF NOT EXISTS users(id INT PRIMARY KEY, username VARCHAR(64), klasse VARCHAR(8), UNIQUE(id, username))''')
db.commit()


def newUser(id, username, klasse):
    c.execute('''INSERT OR IGNORE INTO users(id, username, klasse) VALUES(?,?,?)''', (id, username, klasse))
    db.commit()


def start(bot, update):
    update.message.reply_text('Gebe deine Klasse ein:')

    return KLASSE


def klasse(bot, update):
    user = update.message.from_user
    newUser(user.id, user.username, update.message.text)
    try:
        params = {'cert': 0}
        r = requests.get('http://fbi.gruener-campus-malchow.de/cis/pupilplanapi', params=params)
        vt = json.loads(json.dumps(r.json()))
        update.message.reply_text('Hinweis: Aus Datenschutzgründen können keine Lehrernamen angezeigt werden.')
        for info in vt[0]['Informationen']:
            update.message.reply_text('Informationen:\n\n' + info)
        for n in vt[0][update.message.text]:
            update.message.reply_text('Stunde: ' + vt[0][update.message.text][n]['Stunde'] + '\n' +
                                      'Fach: ' + vt[0][update.message.text][n]['Fach'] + '\n' +
                                      # 'LehrerIn: ' + vt[0][update.message.text][n]['LehrerIn'] + '\n' +
                                      'Raum: ' + vt[0][update.message.text][n]['Raum'] + '\n' +
                                      'Art: ' + vt[0][update.message.text][n]['Art'] + '\n' +
                                      'Hinweis: ' + vt[0][update.message.text][n]['Hinweis'] + '\n')
    except:
        update.message.reply_text('Entweder ist das keine gültige Klasse, oder sie hat heute keine Vertretung.',
                                  reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('Bye', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" verursachte Fehler "%s"' % (update, error))


def main():
    updater = Updater(token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            KLASSE: [MessageHandler(Filters.all, klasse)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    # Startet den Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
