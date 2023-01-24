import os
import shelve
import logging
from environs import Env
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from shop_api import (
    fetch_products, get_product_by_id, client_credentials_access_token, take_product_image_description
)

logger = logging.getLogger(__name__)

IMAGES = 'images'


def start(update, context):

    access_token = context.bot_data['access_token']
    products = fetch_products(access_token)

    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(product['name'], callback_data=product['id'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text='Please choose:', reply_markup=reply_markup)

    return 'HANDLE_MENU'


def product_detail(update, context):

    query = update.callback_query

    access_token = context.bot_data['access_token']
    product = get_product_by_id(access_token, query.data)
    image_url = take_product_image_url(access_token, product)

    text = (
        f'{product["name"]}'
        '\n\n'
        f'Price: {product["price"][0]["amount"]} {product["price"][0]["currency"]}'
        '\n\n'
        f'{product["description"][:200]}...'
    )
    context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_url,
        caption=text
    )
    context.bot.deleteMessage(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )

    return 'START'


def handle_users_reply(update, context):

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        with shelve.open('state') as db:
            user_state = db[str(chat_id)]

    states_functions = {
        'START': start,
        'HANDLE_MENU': product_detail
    }
    state_handler = states_functions[user_state]
    print(state_handler)
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(update, context)

        with shelve.open('state') as db:
            db[str(chat_id)] = next_state
    except Exception as err:
        print(err)



if __name__ == '__main__':

    os.makedirs(IMAGES, exist_ok=True)

    env = Env()
    env.read_env()

    logger.setLevel(logging.INFO)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger.info('Запущен state-bot')

    # Получение токена для работы с интернет-магазином
    client_id = env.str('MOTLIN_CLIENT_ID')
    client_secret = env.str('MOTLIN_CLIENT_SECRET')
    access_token = client_credentials_access_token(client_id, client_secret)

    token = env.str('TG_TOKEN')
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data = {
        'access_token': access_token
    }

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()
