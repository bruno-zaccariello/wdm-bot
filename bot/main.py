import importlib
from telegram.ext import PrefixHandler, CommandHandler, Filters, MessageHandler, Updater, ConversationHandler
from config.settings import TELEGRAM_TOKEN
from impacta.timetable import getFullTimetable
from impacta.gradetable import getNotes

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        PrefixHandler('/', 'horarios', getFullTimetable, pass_args=True)
    )

    grades_handler = ConversationHandler(
        entry_points=[PrefixHandler('/', 'notas', getNotes, pass_args=True)]
    )

    dispatcher.add_handler(
        PrefixHandler('/', 'notas', getNotes, pass_args=True)
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
