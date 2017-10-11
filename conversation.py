from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)

import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '455989974:AAG1_pt549X9YV64asFXixuaMl-lchzidgk'

# 0: choose joke or guess
# 1: choose joke type
# 2: choose guess type
# 3: give score. (END)
CHOOSING, JOKE, GUESS, SCORE = range(4)


def start(bot, update):
    reply_keyboard = [['joke', 'guess']]

    update.message.reply_text(
        "Hi! I'm a Bot, nice to meet you.\n"
        "Send /cancel to stop talking to me\n"
        "Would you like joke or guess ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True)
    )

    return CHOOSING


def joke(bot, update):
    reply_keyboard = [['1', '2', '3']]
    text = update.message.text
    update.message.reply_text("haha, you say %s ?\n" % text)
    return JOKE


def guess(bot, update):
    reply_keyboard = [['1', '2', '3']]
    text = update.message.text
    update.message.reply_text("c8c8, you say %s ?\n" % text)
    return GUESS


def score(bot, update):
    text = update.message.text
    update.message.reply_text("higher")
    return SCORE


def end(bot, update):
    text = update.message.text
    update.message.reply_text("bye bye")
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^joke$', joke),
                       RegexHandler('^guess$', guess)],

            JOKE:  [MessageHandler(Filters.text, score)],
            GUESS: [MessageHandler(Filters.text, score)],
            SCORE: [MessageHandler(Filters.text, end  )],
            },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()