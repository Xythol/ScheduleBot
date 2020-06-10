from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, CallbackQueryHandler
import telegram
import logging
import scheduler
import os

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello sir!")

def main():
    # TOKEN = os.environ.get('TELEGRAM_TOKEN')
    # PORT = os.environ.get('PORT')
    # PLATFORM = os.environ.get('PLATFORM')
    
    # Environment vars
    TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
    PLATFORM = os.getenv("PLATFORM")
    PORT = os.getenv("PORT")

    updater = Updater(token=TELEGRAM_KEY, use_context=True)
    dispatcher = updater.dispatcher
    # job = updater.job_queue


    # Logging init
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Init classes
    scheduleconvo = scheduler.SchedulerConvo()
    reviewreminder = scheduler.ReviewReminders()

    ### CommandHandler
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(scheduleconvo.get_convo_handler())
    dispatcher.add_handler(reviewreminder.get_review_handler())
    
    ### Callback_Query handler
    dispatcher.add_handler(reviewreminder.get_callbackquery_handler())    


    # If on heroku, run webhook
    if PLATFORM == 'HEROKU':
        updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TELEGRAM_KEY)
        updater.bot.set_webhook("https://schedulerbotz.herokuapp.com/" + TELEGRAM_KEY)
    else:
        updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()