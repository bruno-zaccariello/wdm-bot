import importlib
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from config.settings import IMPACTA_PASS, IMPACTA_USER, TELEGRAM_TOKEN

def main():
    updater = Updater(token=TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CommandHandler('horarios', getFullTimetable)
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
