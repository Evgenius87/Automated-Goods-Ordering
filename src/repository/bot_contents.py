import os

from dotenv import load_dotenv
from aiohttp import ClientSession
from aiohttp import ClientSession
from fastapi import FastAPI, Request, APIRouter
from sqlalchemy.orm import Session

from src.schemas import BotUpdateModel, FromTG, BotMessage, StopListModel
from src.database.models import Dish, User, Category
from src.services.telegram_bot import TelegramBot
from src.services.bot_exceptions import bot_exceptions
from src.conf.config import settings
from src.services.handler_errors import handle_errors
from src.services.auth import auth_service
from src.repository.stop_list import get_stop_list


load_dotenv()
TG_API = settings.bot_token

HELLO_MESSAGE = "Вітаємо тебе, новий користувач! \n👋 Ласкаво просимо до нашого телеграм-бота! Ми раді бачити тебе тут. 😊\n📌 У нашому боті ти знайдеш багато корисних функцій та цікавих можливостей. Якщо у тебе виникнуть питання або потрібна буде допомога, не соромся звертатися!\n📚 Бажаємо тобі приємного користування і сподіваємося, що наш бот стане для тебе корисним інструментом.\nГарного дня і чудового настрою! 🌟\n\nЗ повагою,\n\nКоманда [Назва бота] 🤖\n\n[Посилання на сайт]"
ENTER_PASSWORD_MESSAGE = "Введіть код"
PASSWORD_PLACEHOLDER = "4 цифри"
NEGATIVE_MESSAGE = "Невірний пароль, попробуйте ще раз!"
BANNED_MESSAGE = "Вас забанено"

bot = TelegramBot(TG_API)


@bot_exceptions
async def is_user_banned(user: User):

    if user.banned:
        return  True
    
    return False


@bot_exceptions
async def get_current_user(request: BotUpdateModel, db: Session) -> User:
    user = db.query(User).filter(User.chat_id == request.message.from_tg.chat_id).first()

    return user


@bot_exceptions
async def verify_user(request: BotUpdateModel, db: Session):
    users = db.query(User).all()
    request_message = request.message.text
    request_chat_id = request.message.from_tg.chat_id
    for user in users:

        if auth_service.verify_password(request_message, user.secret_code):
            print(f"XXXXX{request_message}XXXX{user.secret_code}")
            user.chat_id = request_chat_id

            if request.message.from_tg.username:
                user.username = request.message.from_tg.username
        
            db.commit()
            db.refresh(user)
            positive_message = f'Вітаю, {user.first_name}.\nВи успішно зарегістровані'
            await bot.delete_message(request.message.from_tg.chat_id, request.message.message_id)
            await bot.send_message(request_chat_id, positive_message)
            return await bot.send_home(request)
        
        else:
            await bot.send_message(request_chat_id, NEGATIVE_MESSAGE)
            await bot.send_message_to_reply(request_chat_id, ENTER_PASSWORD_MESSAGE, PASSWORD_PLACEHOLDER)

    return {"message": "ok"}


@bot_exceptions
async def bot_start(request: BotUpdateModel, db: Session) -> dict:
    chat_id = request.message.from_tg.chat_id
    user = await get_current_user(request, db)
    if not user:
        await bot.send_message(chat_id, HELLO_MESSAGE)
        return await bot.send_message_to_reply(chat_id, ENTER_PASSWORD_MESSAGE, PASSWORD_PLACEHOLDER)
    if user:
        return await bot.send_home(request)


# @bot_exceptions
# async def send_message(request: BotUpdateModel, text: str) -> dict:
#     return await bot.send_message(request.message.from_tg.chat_id, text)


# @bot_exceptions
# async def create_new_user(request: BotUpdateModel, db: Session) -> dict:
#     user = User(username=request.message.from_tg.username, 
#                         first_name=request.message.from_tg.first_name,
#                         last_name=request.message.from_tg.last_name,
#                         chat_id=request.message.from_tg.chat_id,
#                         email='',
#                         password='',
#                         bot_role='user')
#     db.add(user)
#     db.commit()
#     message = f'вітаю, {user.first_name} {user.last_name}, регістрація пройшла успішно'
#     await bot.send_message(request.message.from_tg.chat_id, message)
#     return await bot.send_home(request)


# @bot_exceptions
# async def admin_registration(request: BotUpdateModel, db: Session) -> dict:
#     user = User(username=request.message.from_tg.username, 
#                         first_name=request.message.from_tg.first_name,
#                         last_name=request.message.from_tg.last_name,
#                         chat_id=request.message.from_tg.chat_id,
#                         email='',
#                         password='',
#                         bot_role='admin')
#     db.add(user)
#     db.commit()
#     message = f'вітаю, {request.message.from_tg.first_name} {request.message.from_tg.last_name}, регістрація пройшла успішно'
#     await bot.send_message(request.message.from_tg.chat_id, message)
#     return await bot.send_home(request)


@bot_exceptions
async def stop_list(request: BotUpdateModel, db: Session) -> dict:
    stop_list = await get_stop_list(db)
    stop_list: StopListModel
    stop_list_dishes = stop_list.stop_list
    stop_list_dishes_name = [dish.dish_name for dish in stop_list_dishes]
    buttons = await bot.make_bot_buttons(stop_list_dishes_name, request)
    return await bot.send_bot_message(buttons)


@bot_exceptions
async def get_category(request: BotUpdateModel, db: Session) -> Category:
    category = db.query(Category).filter(Category.name == request.message.text).first()
    return category


@bot_exceptions
async def send_category_child(category: Category, request: BotUpdateModel, db: Session) -> dict:
    dishes = category.dishes
    if dishes:
        dishes_names = [dish.dish_name for dish in dishes]
        buttons = await bot.make_bot_buttons(dishes_names,request)
        await bot.send_bot_message(buttons)
        return {'message': 'ok'}
    child = category.child
    child_names = [child.name for child in child]
    buttons = await bot.make_bot_buttons(child_names, request)
    return await bot.send_bot_message(buttons)


@bot_exceptions
async def get_dish(request: BotUpdateModel, db: Session) ->Dish:
    dish = db.query(Dish).filter(Dish.dish_name == request.message.text).first()
    return dish


@bot_exceptions
async def send_admin_functional(dish_name: str, request: BotMessage) -> dict:
    delele = f'видалити позицію {dish_name}'
    add_stop_list = f'додати у стоп-лист {dish_name}'
    del_from_stop_list = f'видалити зі стоп-листа {dish_name}'
    buttons = await bot.make_bot_buttons([add_stop_list, del_from_stop_list, delele], request)
    return await bot.send_bot_message(buttons)


@bot_exceptions
async def send_dish_info(dish: Dish, chai_id: int) -> dict:
    return await bot.send_dish_info(dish, chai_id)


@bot_exceptions
async def del_dish(dish_name: str,request: BotUpdateModel, db: Session) -> dict:
    dish = db.query(Dish).filter(Dish.dish_name == dish_name).first()
    db.delete(dish)
    db.commit()
    return await bot.send_home(request)


@bot_exceptions
async def add_dish_to_stoplist(request: BotUpdateModel, db: Session) -> dict:
    dish_name = request.message.text.removeprefix('додати у стоп-лист').strip()
    dish = db.query(Dish).filter(Dish.dish_name == dish_name).first()
    dish.stop_list = True
    db.commit()
    db.refresh(dish)
    return await bot.send_home(request)


@bot_exceptions
async def del_dish_from_stoplist(request: BotUpdateModel, db: Session) -> dict:
    dish_name = request.message.text.removeprefix('видалити зі стоп-листа').strip()
    dish = db.query(Dish).filter(Dish.dish_name == dish_name).first()
    dish.stop_list = False
    db.commit()
    return await bot.send_home(request)


@bot_exceptions
async def send_home(request: BotUpdateModel):
    return await bot.send_home(request)





