import logging
import time
import os
import asyncio
import re

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
from config import EVERY_HOURS, TOKEN


logging.basicConfig(filename='queue.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    handlers=[logging.FileHandler('queue.log'), logging.StreamHandler()]
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class Sleeper:
    """Class to stop the process after a certain time."""
    def __init__(self):
        self.should_stop = False

    async def sleep(self, seconds):
        for _ in range(seconds):
            if self.should_stop:
                break
            await asyncio.sleep(1)

    def stop(self):
        self.should_stop = True


async def blocking_code(hours):
    print('Starting blocking code.')
    await time.sleep(hours*30)
    print('Finished blocking code.')


INFO, STATUS = range(2)

def is_valid_url(url):
    pattern = re.compile(r'https://[^.]+\.kdmid\.ru/queue/OrderInfo\.aspx\?id=\d+&cd=[A-Fa-f0-9]+')
    return bool(pattern.match(url))

def get_user_info(user_info):
    if user_info.startswith('http'): 
        if not is_valid_url(user_info):
            return None, None, None
        
        user_info = user_info.strip()
        kdmid_subdomain = user_info.split('/')[2].split('.')[0]
        order_id = user_info.split('=')[1].split('&')[0]
        code = user_info.split('=')[-1]
    else:
        kdmid_subdomain, order_id, code = None, None, None
    return kdmid_subdomain, order_id, code

def get_url(kdmid_subdomain, order_id, code):
    return 'http://'+kdmid_subdomain+'.kdmid.ru/queue/OrderInfo.aspx?id='+order_id+'&cd='+code


# TODO interactive buttons for the user to start the process, cancel the process

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation and asks the user about their gender."""

    await update.message.reply_text(
        "Привет! Это бот для автоматической проверки статуса очереди в Консульство РФ в любом городе в любой стране, где есть российское консульство.\n"
        "Скопируйте сюда ссылку для записи на прием и проверки Вашей заявки - в письме от queue-robot@kdmid.ru 'Запись в список ожидания' \n"
        "Например: https://warsaw.kdmid.ru/queue/OrderInfo.aspx?id=85914&cd=824D737D \n\n" 
        "В случае успеха, вам придет письмо на укзанный при регистрации адрес. Время ожидания -- от нескольких часов до нескольких суток. \n\n"
        "Это абсолютно БЕСПЛАТНО\n\n"
    )
    return INFO


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Processes the info from the user."""
    bot = context.bot
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    user_info = update.message.text 
    user_info = user_info.strip()

    kdmid_subdomain, order_id, code = get_user_info(user_info)

    if not kdmid_subdomain or not order_id or not code:
        await bot.send_message(chat_id, 'Что-то не так со ссылкой, проверьте ссылку и попробуйте еще раз.')
        return INFO
    
    await bot.send_message(chat_id, 'Начинаю проверку...')

    # Example of ULR https://barcelona.kdmid.ru/queue/OrderInfo.aspx?id=236043&cd=4D90364D
    # https://warsaw.kdmid.ru/queue/OrderInfo.aspx?id=85914&cd=824D737D
    # barcelona, 236043, 4D90364D

    #### the checking iteration starts ####
    sleeper = Sleeper()

    checker = QueueChecker(kdmid_subdomain, order_id, code)
    success = False
    # iterate until the success/error file is written and success variable changes to True
    while not success:
        # goes to the website of the indicated consulate, checks for a timeslot, returns a message with a status
        message = checker.check_queue()
        await bot.send_message(chat_id, f"{message}") 
        # stop the process if the success/error file is written
        if os.path.isfile(os.path.join(checker.directory, "success.json")) or os.path.isfile(os.path.join(checker.directory, "error.json")):
            success = True   
        # repeat the process after a pause
        if not success: 
            # time.sleep(EVERY_HOURS*3600)  # Pause for every_hours * hour before the next check. One hour is 3600 seconds
            # await blocking_code(EVERY_HOURS*3600)
            await sleeper.sleep(EVERY_HOURS*3600)
    
    await bot.send_message(chat_id, f"Проверка очереди закончилась: {message}") # should not appear before While ends
                      

    if os.path.isfile(os.path.join(checker.directory, "success.json")):
        os.remove(os.path.join(checker.directory, "success.json"))
    if os.path.isfile(os.path.join(checker.directory, "error.json")):
        os.remove(os.path.join(checker.directory, "error.json"))
    return ConversationHandler.END # may be shouldn't be the end?

# TODO user should have some possibility to cancel the process 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    Sleeper().stop()
    await update.message.reply_text("Вы отменили проверку очереди")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    sleeper = Sleeper()
    application = Application.builder().token(TOKEN).concurrent_updates(True).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT  & ~filters.COMMAND, info))
    # Run the bot until Ctrl-C
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        # Stop the sleeper when Ctrl+C is pressed
        sleeper.stop()

    # application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
