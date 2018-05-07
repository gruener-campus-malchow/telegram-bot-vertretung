import logging
import json
import requests
from telegram import (ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KLASSE = range(1)


def start(bot, update):
    user = update.message.from_user
    update.message.reply_text('Gebe deine Klasse ein:')

    return KLASSE


def klasse(bot, update):
    try:
        params = {'cert': 0}
        r = requests.get('http://fbi.gruener-campus-malchow.de/cis/pupilplanapi', params=params)
        vt = json.loads(json.dumps(r.json()))
        for n in vt[0][update.message.text]:
            update.message.reply_text('Stunde: ' + vt[0][update.message.text][n]['Stunde'] + '\n' +
                                      'Fach: ' + vt[0][update.message.text][n]['Fach'] + '\n' +
                                      'LehrerIn: ' + vt[0][update.message.text][n]['LehrerIn'] + '\n' +
                                      'Raum: ' + vt[0][update.message.text][n]['Raum'] + '\n' +
                                      'Art: ' + vt[0][update.message.text][n]['Art'] + '\n' +
                                      'Hinweis: ' + vt[0][update.message.text][n]['Hinweis'] + '\n')
    except:
        update.message.reply_text('Entweder ist das keine gültige Klasse, oder sie hat heute keine Vertretung.')

    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text('Bye', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" verursachte Fehler "%s"' % (update, error))


def main():
    # Bot-Token hier einfügen
    updater = Updater("")

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
