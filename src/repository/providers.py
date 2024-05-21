import os

from dotenv import load_dotenv
from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import BotUpdateModel
from src.database.models import  Provider, User
from src.services.resto_stock_balanse import  IikoAPIHandler
from src.services.telegram_bot import TelegramBot
from src.repository.tags import find_tags


load_dotenv()


TG_API = os.getenv("BOT_TOKEN_PRO")

INPUT_NAME = "Введіть своє ім'я"
INPUT_COMPANY_NAME = "Введіть назву компанії"
INPUT_PHONE = "Введіть номер телефону"
INPUT_EMAIL = "Введіть email"
PLACEHOLDER_NAME = "Your Name"
PLACEHOLDER_COMPANY = "Company"
PLACEHOLDER_PHONE = "Phone"
PLACEHOLDER_EMAIL = "Email"
NICE_TO_MEET_YOU = "Дякую за регістрацію.\nОчікуйте на замовлення"
ORDER_ACCEPTED = "Замовлення отримано"


telegram_bot = TelegramBot(TG_API)


async def get_providers(db: Session):
    providers = db.query(Provider).all()
    return providers


async def delete_provider(id: int, db: Session):
    provider = db.query(Provider).filter(Provider.id == id).first()
    if provider:
        db.delete(provider)
        db.commit()
    return {"message": "provider successfully deleted"}


async def start_message(request: BotUpdateModel, db: Session):
    provider = Provider(
        username = request.message.from_tg.username,
        first_name = request.message.from_tg.first_name,
        chat_id = request.message.from_tg.chat_id
    )
    db.add(provider)
    db.commit()
    print("start_message")
    return await telegram_bot.send_message_to_reply(chat_id=request.message.from_tg.chat_id,
                                                    message=INPUT_NAME,
                                                    placeholder=PLACEHOLDER_NAME)


async def save_provider_name(request: BotUpdateModel, db: Session):
    provider = db.query(Provider).filter(Provider.chat_id == request.message.from_tg.chat_id).first()
    provider.salesman_name = request.message.reply_to_message.text
    db.commit()
    return await telegram_bot.send_message_to_reply(chat_id=request.message.from_tg.chat_id,
                                                    message=INPUT_COMPANY_NAME,
                                                    placeholder=PLACEHOLDER_COMPANY)



async def save_provider_company(request: BotUpdateModel, db: Session):
    provider = db.query(Provider).filter(Provider.chat_id == request.message.from_tg.chat_id).first()
    provider.provider_name = request.message.reply_to_message.text
    db.commit()
    return await telegram_bot.send_message_to_reply(chat_id=request.message.from_tg.chat_id,
                                                    message=INPUT_PHONE,
                                                    placeholder=PLACEHOLDER_PHONE)


async def save_provider_phone(request: BotUpdateModel, db: Session):
    provider = db.query(Provider).filter(Provider.chat_id == request.message.from_tg.chat_id).first()
    provider.salesman_phone = request.message.reply_to_message.text
    db.commit()
    return await telegram_bot.send_message_to_reply(chat_id=request.message.from_tg.chat_id,
                                           message=INPUT_EMAIL, placeholder=PLACEHOLDER_EMAIL)


async def save_provider_email(request: BotUpdateModel, db: Session):
    provider = db.query(Provider).filter(Provider.chat_id == request.message.from_tg.chat_id).first()
    provider.salesman_email = request.message.reply_to_message.text
    db.commit()
    user = db.query(User).filter(User.email == request.message.reply_to_message.text)
    if user:
        provider.user = user
        user.forward_provider_message = True
    db.commit()
    return await telegram_bot.send_message(chat_id=request.message.from_tg.chat_id,
                                           message=NICE_TO_MEET_YOU)


async def forward_message_to_admin(request: BotUpdateModel, db: Session):
    providers = db.query(Provider).filter(Provider.user.forward_provider_message == True).all()
    current_provider = db.query(Provider).filter(Provider.chat_id == request.message.from_tg.chat_id).first()
    salesman_name = current_provider.salesman_name
    provider_name = current_provider.provider_name
    message = f"Повідомлення від\n{provider_name}\n{salesman_name}:\n{request.message.text}"
    for provider in providers:
        await telegram_bot.send_message(chat_id=provider.chat_id,
                                        message=message)
        return {"message": "Ok"}


