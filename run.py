from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)

import logging
import time
import Beauty
import Cardcode

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '455989974:AAG1_pt549X9YV64asFXixuaMl-lchzidgk'
PTT_URL = 'https://www.ptt.cc'


START, BEAUTY, DECK, GUESS, END = range(5)


def showBeauty(bot, update):
    global index
    global beauty_articles
    global beauty_img_urls

    if index >= len(beauty_articles):
        update.message.reply_text("there is no more beauty today")
        return START
    
    while(beauty_articles[index]['push_count']<0):
        index = index + 1

    article = beauty_articles[index]
    page = Beauty.get_web_page(PTT_URL + article['href'])
    if page:
        beauty_img_urls = Beauty.parse_img(page)
    
    img_url = beauty_img_urls
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=img_url[0])

    # reply and show keyboard choice
    reply_keyboard = [['OK', 'next']]

    update.message.reply_text(
        "do you like this one ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True)
    )

    index = index + 1
    return BEAUTY


def allBeauty(bot, update):
    global beauty_img_urls

    chat_id = update.message.chat_id
    for url in beauty_img_urls:
        if url == beauty_img_urls[0]:
            continue
        bot.send_photo(chat_id=chat_id, photo=url)

    return END


def getDeck(bot, update):
    deck_codes = Cardcode.get_deck_code()
    chat_id = update.message.chat_id

    for code in deck_codes:
        bot.send_message(chat_id=chat_id, text=code)
    
    bot.send_message(chat_id=chat_id, text="say something to me")
    return END


def guess(bot, update):
    reply_keyboard = [['0', '5', '10']]
    update.message.reply_text("哪個殺手只會講英文 ?? (給你五秒唷)")
    time.sleep(5)
    update.message.reply_text("銀翼殺手")
    update.message.reply_text(
        "請給分",        
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )
    return END


def start(bot, update):
    # reply and show keyboard choice
    reply_keyboard = [['beauty', 'code', 'guess']]

    update.message.reply_text(
        "/cancel to stop conversation.\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True)
    )

    return START


def end(bot, update):
    text = update.message.text
    update.message.reply_text("you say %s, i say goodbye." % text)
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
    # init variable for Beauty
    global index
    global beauty_articles
    
    index = 0
    beauty_articles = Beauty.get_today_articles()

    # set parameter for bot
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # initial state (recieve '/start', then go start())
        entry_points=[CommandHandler('start', start)],

        states={
            START: [RegexHandler('^beauty$', showBeauty),
                    RegexHandler('^code$', getDeck),
                    RegexHandler('^guess$', guess)],

            BEAUTY: [RegexHandler('^OK$', allBeauty),
                    RegexHandler('^next$', showBeauty)],

            DECK: [MessageHandler(Filters.text, end)],
            GUESS:[MessageHandler(Filters.text, end)],

            END: [MessageHandler(Filters.text, end)]
            },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()
