from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

from datetime import datetime
from mongodb import MongoDB

import json
from bson.objectid import ObjectId

class SchedulerConvo:
    DESCRIPTION, DATE, TIME = range(3)

    description_val = ""
    year_val = 0
    month_val = 0
    day_val = 0
    hour_val = 0
    minute_val = 0

    date_val = 0
    time_val = 0

    def start(self, update, context):
        reply_message = "Please enter a description for the schedule."

        update.message.reply_text(reply_message)

        return self.DESCRIPTION

    def cancel(self, update, context):
        update.message.reply_text("You have exited out of the dialog.")

        return ConversationHandler.END

    def description(self, update, context):
        # Handles convo cancellation
        if update.message.text == "/cancel":
            update.message.reply_text("You have stopped scheduling for a reminder.")
            return ConversationHandler.END
        
        self.description_val = update.message.text

        reply_message = "Please enter the date(ddmmyyyy) of reminder."

        update.message.reply_text(reply_message)

        return self.DATE

    def date(self, update, context):
        # Handles convo cancellation
        if update.message.text == "/cancel":
            update.message.reply_text("You have stopped scheduling for a reminder.")
            return ConversationHandler.END

        # check if there are 8 numbers in the str
        message_date = update.message.text

        if len(message_date) != 8 or message_date.isdigit() == False:
            update.message.reply_text("Please check that you have entered 8 numbers.")

            return self.DATE

        day = message_date[0:2]
        month = message_date[2:4]
        year = message_date[4:8]

        # Check if date is current date or later
        current_date = datetime.now().date()
        input_date = datetime(int(year), int(month), int(day)).date()

        if current_date > input_date:
            update.message.reply_text("You have entered a date before today. Please re-enter the date(ddmmyyyy).")

            return self.DATE

        # store the date in memory for time check
        self.day_val = day
        self.month_val = month
        self.year_val = year

        # store the date in memory to be written into db
        self.date_val = message_date

        update.message.reply_text("Please enter the time(24 hours E.g 0100) that you would like to have the reminder.")

        return self.TIME

    def time(self, update, context):
        # Handles convo cancellation
        if update.message.text == "/cancel":
            update.message.reply_text("You have stopped scheduling for a reminder.")
            return ConversationHandler.END

        # check if there are 8 numbers in the str
        message_time = update.message.text

        if len(message_time) != 4 or message_time.isdigit() == False:
            update.message.reply_text("Please check that you have entered 4 numbers.")

            return self.TIME

        hour = message_time[0:2]
        minute = message_time[2:4]

        # Check if date is current date or later including the time
        current_date = datetime.now()
        input_date = datetime(int(self.year_val), int(self.month_val), int(self.day_val), int(hour), int(minute))

        if current_date > input_date:
            update.message.reply_text("You have entered a time in the past. Please re-enter the time(24 hours).")

            return self.TIME

        # store hour and minute for display
        self.hour_val = hour
        self.minute_val = minute

        # store the time in memory before writing into the database
        self.time_val = message_time

        reply_message = "Description: {0}\nDate(Day/Month/Year): {1}/{2}/{3}\nTime(hh:mm): {4}:{5}".format(self.description_val, self.day_val, self.month_val, self.year_val, self.hour_val, self.minute_val)
        update.message.reply_text(reply_message)

        # Init mongodb connection
        db = MongoDB('heroku_mqncqpgt', 'reminders')
        db.insertonedb({"chatid" : update.message.chat.id, "description" : self.description_val, "date" : self.date_val, "time" : self.time_val})

        return ConversationHandler.END


    def get_convo_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler("createreminder", self.start)],
            states={
                self.DESCRIPTION: [MessageHandler(Filters.text, self.description)],
                self.DATE: [MessageHandler(Filters.text, self.date)],
                self.TIME: [MessageHandler(Filters.text, self.time)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )

#####################################################################################################################################################

# Deserializer object
# class ReminderObject:
#     def __init__(self, jsonstr):
#         self.__dict__ = json.loads(jsonstr)

class ReviewReminders:

    def __init__(self):
        # Init database
        self.db = MongoDB('heroku_mqncqpgt', 'reminders')

    def showallreminders(self, update, context):
        # get the chat id to retrieve all reminders for that chat
        chatid = update.message.chat.id

        query = { "chatid" : chatid }

        for element in self.db.finddb(query):

            # separate the date str
            day = element["date"][0:2]
            month = element["date"][2:4]
            year = element["date"][4:8]

            # separate the time str
            hour = element["time"][0:2]
            minute = element["time"][2:4]

            id = str(element["_id"])

            messagestr = "Description: {0}\nDate(Day/Month/Year): {1}/{2}/{3}\nTime(hh:mm): {4}:{5}\noid: {6}".format(element["description"], day, month, year, hour, minute, str(element["_id"]))

            # Add inlinebutton
            keyboard = [[InlineKeyboardButton("Delete from database", callback_data='delete')]]

            update.message.reply_text(messagestr, reply_markup = InlineKeyboardMarkup(keyboard))


    def get_review_handler(self):
        return CommandHandler("allreminder", self.showallreminders)

    def reminder_button(self, update, context):
        # if is delete button
        if update.callback_query.data == "delete":
            callback_message = update.callback_query.message

            # Retrieve the objectid str from the message
            objectidstr = callback_message.text.split("\n")[3].split(":")[1].strip()

            # Convert object id str into ObjectID
            objectid = ObjectId(objectidstr)

            # Delete from db
            query = { "_id" : objectid }
            self.db.deleteonedb(query)

            # Delete the message
            context.bot.delete_message(chat_id = update.effective_chat.id, message_id = update.callback_query.message.message_id)

    def get_callbackquery_handler(self):
        return CallbackQueryHandler(self.reminder_button)