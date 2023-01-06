import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, Updater

from app import yadict
from app.templates import MessageTemplate

load_dotenv()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def translate(update: Update, context) -> None:
    # chat_id = update.message.chat_id
    # update.message.reply_text(text='588607279')
    content, warning = yadict.normalize(update.message.text[3:])
    if warning:
        update.message.reply_text(text=content)
        return
    answer = yadict.load_content_from_api(content)
    if not answer:
        update.message.reply_html(text=MessageTemplate.CANT_FIND.format(content))
        return
    update.message.reply_markdown_v2(text=answer)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("BOT_TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("tr", translate))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
