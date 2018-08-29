import json
import logging
import sqlite3

import requests
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
    user = update.message.from_user
    try:
        c.execute('''SELECT klasse FROM users WHERE id = ?''', (user.id,))
        sendplan(bot, user.id, c.fetchone()[0])
        return ConversationHandler.END
    except:
        update.message.reply_text('Gebe deine Klasse ein:')
        return KLASSE


def klasse(bot, update):
    user = update.message.from_user
    newUser(user.id, user.username, update.message.text)
    sendplan(bot, user.id, update.message.text)
    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('Bye', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def delklasse(bot, update):
    user = update.message.from_user
    try:
        c.execute('''DELETE FROM users WHERE id = ?''', (user.id,))
        db.commit()
        update.message.reply_text('Daten erfolgreich gelöscht')
    except:
        update.message.reply_text('Irgendwas ging schief')


# def setkurse(bot, update, args):
#     print(args)


def sendplan(bot, userid, userklasse):
    try:
        params = {'cert': 0}
        r = requests.get('http://fbi.gruener-campus-malchow.de/cis/pupilplanapi', params=params)
        vt = json.loads(json.dumps(r.json()))
        update.message.reply_text('Hinweis: Aus Datenschutzgründen können keine Lehrernamen angezeigt werden.')
        for info in vt[0]['Informationen']:
            update.message.reply_text('Informationen:\n\n' + info)
        for n in vt[0][userklasse]:
            update.message.reply_text('Stunde: ' + vt[0][userklasse][n]['Stunde'] + '\n' +
                                      'Fach: ' + vt[0][userklasse][n]['Fach'] + '\n' +
                                      # 'LehrerIn: ' + vt[0][userklasse][n]['LehrerIn'] + '\n' +
                                      'Raum: ' + vt[0][userklasse][n]['Raum'] + '\n' +
                                      'Art: ' + vt[0][userklasse][n]['Art'] + '\n' +
                                      'Hinweis: ' + vt[0][userklasse][n]['Hinweis'] + '\n')
    except:
        bot.sendMessage(chat_id=userid,
                        text='Entweder ist das keine gültige Klasse, oder sie hat heute keine Vertretung.',
                        reply_markup=ReplyKeyboardRemove())


def updateAnAlle(bot, job):
    c.execute('''SELECT * FROM users''')
    for user in c.fetchall():
        sendplan(bot, user[0], user[2])


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
    delklasseHandler = CommandHandler('delklasse', delklasse)
    dp.add_handler(delklasseHandler)

    # Startet den Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
