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

with open('token.key', 'r') as fh:
    data = fh.read()
    # print(data)

TOKEN = data.strip()

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

INFO, STATUS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation and asks the user about their gender."""

    await update.message.reply_text(
        "Привет! Это бот для автоматической проверки статуса очереди в Консульство РФ в любом городе.\n"
        "Вы можете прислать данные для проверки в одном из двух форматах: \n\n"
        "1 - ссылка для записи на прием и проверки Вашей заявки - в письме от queue-robot@kdmid.ru 'Запись в список ожидания' \n"
        "Например: https://warsaw.kdmid.ru/queue/OrderInfo.aspx?id=85914&cd=824D737D \n\n" 
        "2 - через запятую латинскими буквами: город (как в командной строке), номер заявки, защитный код\n"
        "Например: madrid, 130238, 8367159E\n"
        "В случае успеха, вам придет письмо на укзанный при регистрации адрес.\n"
        "Это абсолютно БЕСПЛАТНО\n\n"
        "Чтобы начать, напишите /start"
    )
    return INFO


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Stores the info from the user."""
    user_info = update.message.text
    print(user_info)
        # https://warsaw.kdmid.ru/queue/OrderInfo.aspx?id=85914&cd=824D737D
    if user_info.startswith('http'): 
        print(user_info.split('/'))
        kdmid_subdomain = user_info.split('/')[2].split('.')[0]
        order_id = user_info.split('=')[1].split('&')[0]
        code = user_info.split('=')[-1]
        print(kdmid_subdomain)
        print(order_id, code)
    else: 
        kdmid_subdomain, order_id, code = user_info.strip().split(',')
        kdmid_subdomain = kdmid_subdomain.strip()
        order_id = order_id.strip()
        code = code.strip()
        if kdmid_subdomain is None or order_id is None or code is None: 
            await update.message.reply_text(f"Please try again")

    success_file = order_id+"_"+code+"_success.json"
    error_file = order_id+"_"+code+"_error.json"

    checker = QueueChecker()

    success = False

    while not success:

        message, status = checker.check_queue(kdmid_subdomain, order_id, code)
        await update.message.reply_text(f"Queue checking status: {message}")

        if os.path.isfile(success_file) or os.path.isfile(error_file):
            success = True

        if not success: 
            time.sleep(1*60)  # Pause for every_hours * hour before the next check
    
    await update.message.reply_text(f"Result: {message}") # should not appear befor While ends

    return ConversationHandler.END # may be shouldn't be the end?


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