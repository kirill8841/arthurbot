import re
import time

import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from fighter_templates import fighter_keyboard
from bibler_templates import bibler_keyboard
from processor import Arthur

# Defining the names of modes
DEFAULT, FIGHT, BIBLE = range(3)


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    """ The function that will be called exactly once - when /start is called.
        It also initialises an instance of Arthur class, so that if we restart
        the bot via commands without turning off the programme its stats are
        reinitialised.
    """
    update.message.reply_text('Здорова сучки, я вернулся!')
    global arthur
    arthur = Arthur()

    return DEFAULT


def fighter(update, context):
    global arthur

    fight_response = arthur.fight(update.message.text)

    # Written without these lines it doubles the message when passing from one mode to another
    if not 'next_mode' in fight_response:
        update.message.reply_text(
            fight_response['text'], reply_markup=ReplyKeyboardMarkup(fighter_keyboard))

    if 'next_mode' in fight_response:
        update.message.reply_text(
            fight_response['text'], reply_markup=ReplyKeyboardRemove())
        return fight_response['next_mode']

    return None


def dealer(update, context):
    """ The function to give responses in the DEFAULT mode using Arthur class
        and link it with Telegram API using python-telegram-bot wrapper.
        Also checks if the Arthur.deal returned a new mode to pass to.
    """
    global arthur
    deal_response = arthur.deal(update.message.text)
    if not 'next_mode' in deal_response:
        update.message.reply_text(deal_response['text'])
    if 'next_mode' in deal_response:
        if deal_response['next_mode'] == 1:
            update.message.reply_text(
                "Ану только спизданите что-то", reply_markup=ReplyKeyboardMarkup(fighter_keyboard))
        elif deal_response['next_mode'] == 2:
            return bibler_command(update, context)

        return deal_response['next_mode']

    return None


def bibler(update, context):
    """ A function to connect ConversationHandler's BIBLE mode with
        Arthur class.
    """
    global arthur
    bible_response = arthur.bible(update.message.text)

    # i.e. no template matched
    if bible_response == None:
        return None

    if not 'next_mode' in bible_response:
        if 'normal' in bible_response:
            update.message.reply_text("Так, что тут у нас...")
            time.sleep(0.5)
        update.message.reply_text(
            bible_response['text'], reply_markup=ReplyKeyboardMarkup(bibler_keyboard))

    if 'next_mode' in bible_response:
        update.message.reply_text(
            "Я бы вам еще погадал...", reply_markup=ReplyKeyboardRemove())
        return bible_response['next_mode']

    return None


def bibler_command(update, context):
    """ A function to pass to bible mode via /bible command. 
        Without it, 'bibler' function won't show the keyboard at once.
    """
    update.message.reply_text(
        "Сейчас будем гадать, дети", reply_markup=ReplyKeyboardMarkup(bibler_keyboard))
    return 2


def cancel(update, context):
    """ The function that is called when /cancel is entered in the chat """
    update.message.reply_text("Ну пока", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    """ The main function that initializes an instance of Arthur and takes
        advantage of python-telegram-bot wrapper to connect with Telegram API.
        ConversationHandler class is used for this programme, which means
        there may be different modes(states) of conversation. The bot will
        be on on two conditions:
        1) Main module is running (no errors)
        2) /start command has been entered in the chat. Once /cancel is
        entered, the bot stops responding.
    """
    global arthur

    # Initialising an Updater using out bot's authorisation token
    updater = Updater(
        "957035218:AAHfWFPNd38-qE3v81dLg_xOTwEr6llcgGs", use_context=True)
    dp = updater.dispatcher

    # The entry_points argument is a list of handlers that will be launched
    # once at the start of the programme. States argument are modes that
    # would be avaliable in the conversation. The fallbacks argument is a list
    # of handlers that are called when no other handlers were used.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            DEFAULT: [MessageHandler(Filters.regex(re.compile(r'артур|певец', flags=re.I)), dealer)],

            # Match everything but a command starting with /
            FIGHT: [MessageHandler(Filters.regex(re.compile(r'^(?!/).*$')), fighter)],

            BIBLE: [MessageHandler(Filters.regex(
                re.compile(r'^(?!/).*$')), bibler)]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   CommandHandler('bible', bibler_command)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
