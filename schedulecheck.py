from mongodb import MongoDB
from datetime import datetime
import os

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

class schedulecheck:

    TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
    PLATFORM = os.getenv("PLATFORM")
    PORT = os.getenv("PORT")

    updater = Updater(token=TELEGRAM_KEY, use_context=True)

    @staticmethod
    def check_schedules():
        print (schedulecheck.updater)
        db = MongoDB('heroku_mqncqpgt', 'reminders')

        # Get all reminders today.
        current_date = datetime.now().date().strftime('%d%m%Y')
        query = { "date" : current_date }

        for element in db.finddb(query):

                # separate the date str
                day = element["date"][0:2]
                month = element["date"][2:4]
                year = element["date"][4:8]

                # separate the time str
                hour = element["time"][0:2]
                minute = element["time"][2:4]

                chatid = element["chatid"]

                messagestr = "Description: {0}\nDate(Day/Month/Year): {1}/{2}/{3}\nTime(hh:mm): {4}:{5}\noid: {6}".format(element["description"], day, month, year, hour, minute, str(element["_id"]))

                schedulecheck.updater.bot.send_message(chatid, messagestr)



if __name__ == '__main__':
    schedulecheck.check_schedules()