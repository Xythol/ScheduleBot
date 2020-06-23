from mongodb import MongoDB
from datetime import datetime
import os
from bson.objectid import ObjectId

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

        # Get current time
        current_time = datetime.now().strftime("%H%M")

        # Loop through all reminders today to check for the time
        for element in db.finddb(query):

                # separate the date str
                # day = element["date"][0:2]
                # month = element["date"][2:4]
                # year = element["date"][4:8]

                # separate the time str
                hour = int(element["time"][0:2])
                minute = int(element["time"][2:4])

                # Convert hour and minute into datetime
                remindertime = datetime.now().replace(hour=hour, minute=minute).strftime("%H%M")

                # If remindertime is less than current timing, send out timing and delete the reminder from DB
                if remindertime <= current_time:
                    chatid = element["chatid"]

                    messagestr = "Reminder: {0}".format(element["description"])

                    schedulecheck.updater.bot.send_message(chatid, messagestr)

                    # Convert object id str into ObjectID
                    objectid = ObjectId(str(element["_id"]))

                    # Delete from db
                    query = { "_id" : objectid }
                    db.deleteonedb(query)



if __name__ == '__main__':
    schedulecheck.check_schedules()