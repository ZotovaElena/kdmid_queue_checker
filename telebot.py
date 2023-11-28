import logging
import time
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from core.queue_checker import QueueChecker

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = 'YOUR_TOKEN'

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

INFO, STATUS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation and asks the user about their gender."""

    await update.message.reply_text(
        "Это бот для автоматической проверки статуса очереди в Консульство РФ \n"
        "Вы можете прислать данные для проверки в одном из двух форматах: \n\n"
        "1) ссылка для записи на прием и проверки Вашей заявки - в письме от queue-robot@kdmid.ru 'Запись в список ожидания' \n"
        "2) через запятую ЛАТИНСКИМИ буквами: город, номер заявки, защитный код"
    )
    return INFO


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Stores the info from the user."""
    user_info = update.message.text
    print(user_info)

    kdmid_subdomain, order_id, code = user_info.strip().split(',')
    
    success_file = order_id+"_"+code+"_success.json"
    error_file = order_id+"_"+code+"_error.json"

    checker = QueueChecker()

    while True:

        message, status = checker.check_queue(kdmid_subdomain, order_id, code)
        await update.message.reply_text(f"Queue checking status: {message}")

        if os.path.isfile(success_file) or os.path.isfile(error_file):
            break

        time.sleep(1*30)  # Pause for every_hours * hour before the next check
    
    await update.message.reply_text(f"Result: {message}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states INFO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INFO: [MessageHandler(filters.TEXT  & ~filters.COMMAND, info)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()