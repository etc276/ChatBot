from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)

import logging
import time
import Beauty
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '455989974:AAG1_pt549X9YV64asFXixuaMl-lchzidgk'
PTT_URL = 'https://www.ptt.cc'


START, BEAUTY, JOKE, GUESS, END = range(5)

index = None;

def findBeauty():
    global beauty_articles
    global beauty_img_urls

    beauty_articles = []
    beauty_img_urls = []

    current_page = Beauty.get_web_page(PTT_URL + '/bbs/Beauty/index.html')
    if current_page:
        articles = []  # 全部的今日文章
        date = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
        current_articles, prev_url = Beauty.get_articles(current_page, date)  # 目前頁面的今日文章
        while current_articles:  # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
            articles += current_articles
            current_page = Beauty.get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = Beauty.get_articles(current_page, date)

        beauty_articles = articles
        print("num of article: ", len(articles))


def showBeauty(bot, update):
    global index
    global beauty_articles
    global beauty_img_urls

    if index >= len(beauty_articles):
        update.message.reply_text("there is no more beauty today")
        return START
        
    article = beauty_articles[index]
    if(article['push_count'] < 0):
        index = index + 1;
        showBeauty;
    page = Beauty.get_web_page(PTT_URL + article['href'])
    if page:
        beauty_img_urls = Beauty.parse(page)
    
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
        bot.send_photo(chat_id=chat_id, photo=url)

    return END


def joke(bot, update):
    reply_keyboard = [['0', '5', '10']]
    update.message.reply_text(
        "haha",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )

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
    reply_keyboard = [['beauty', 'joke', 'guess']]

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
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    global index
    index = 0

    findBeauty()

    conv_handler = ConversationHandler(
        # initial state (recieve '/start', then go start())
        entry_points=[CommandHandler('start', start)],

        states={
            START: [RegexHandler('^beauty$', showBeauty),
                    RegexHandler('^joke$', joke),
                    RegexHandler('^guess$', guess)],

            BEAUTY: [RegexHandler('^OK$', allBeauty),
                    RegexHandler('^next$', showBeauty)],

            JOKE: [MessageHandler(Filters.text, end)],
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
