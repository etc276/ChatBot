from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

OPTIONS, PHOTO, TEXT, PHONE = range(4)

def start(bot, update):
	reply_keyboard = [['Imagem', 'Texto']]
	update.message.reply_text('Olá, escolha uma das opções abaixo:', 
		reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	
	return OPTIONS


def options(bot, update):
	user = update.message.from_user
	logger.info("Option of %s: %s" % (user.first_name, update.message.text))

	#Selected upload image
	if update.message.text == 'Imagem':
		update.message.reply_text('Me envie uma foto, para ser postada em sua timeline', 
			reply_markup=ReplyKeyboardRemove())
		return PHOTO
	else:
		update.message.reply_text('Me envie o texto, para ser postado em sua timeline', 
			reply_markup=ReplyKeyboardRemove())
		return TEXT


def get_photo(bot, update, user_data):
	user = update.message.from_user
	photo_file = bot.get_file(update.message.photo[-1].file_id)
	#photo_file.download('user_photo.jpg')
	logger.info("Photo of %s: %s" % (user.first_name, 'user_photo.jpg'))

	user_data['photo'] = photo_file

	contact_keyboard = KeyboardButton("Compartilhar telefone", request_contact=True)
	custom_keyboard = [[contact_keyboard]]
	reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

	update.message.reply_text('Para completar o processo, preciso do seu telefone, pode me enviar?',
		reply_markup=reply_markup)
	return PHONE


def get_text(bot, update, user_data):
	user = update.message.from_user
	logger.info("Text of %s: %s" % (user.first_name, update.message.text))

	user_data['text'] = update.message.text
	
	contact_keyboard = KeyboardButton("Compartilhar telefone", request_contact=True)
	custom_keyboard = [[contact_keyboard]]
	reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

	update.message.reply_text('Para completar o processo, preciso do seu telefone, pode me enviar?',
		reply_markup=reply_markup)
	
	return PHONE


def get_phone(bot, update, user_data):
	print ('entrou')
	user_contact = update.message.contact
	logger.info('Contact of %s: %s' % (user_contact.first_name, user_contact.phone_number))
	update.message.reply_text('Postado em sua timeline! O Fatalmodel lhe deseja muito sucesso!', 
		reply_markup=ReplyKeyboardRemove())
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
	# Create the EventHandler and pass it your bot's token.
	updater = Updater("455989974:AAG1_pt549X9YV64asFXixuaMl-lchzidgk")

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add conversation handler with the states GENDER, PHOTO, LOCATION and text
	conv_handler = ConversationHandler(
		entry_points = [CommandHandler('start', start)],
		states=
		{
			OPTIONS: [RegexHandler('^(Imagem|Texto)$', options)],
			
			PHOTO: [MessageHandler(Filters.photo, get_photo, pass_user_data=True)],
			
			TEXT: [MessageHandler(Filters.text, get_text, pass_user_data=True)],

			PHONE: [MessageHandler(Filters.contact, get_phone, pass_user_data=True)]
		},
		fallbacks = [CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()