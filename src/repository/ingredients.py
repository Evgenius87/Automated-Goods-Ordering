import os
import logging
import time

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.schemas import OrederIngByProvider, IngredientUpdateModel, FromTG, FakeBotUpdateModel, FakeBotRequest
from src.database.models import Ingredient, Provider
from src.services.resto_stock_balanse import  IikoAPIHandler
from src.services.telegram_bot import TelegramBot
from src.services.handler_errors import handle_errors




load_dotenv()


TG_API = os.getenv("BOT_TOKEN_PRO")


telegram_bot = TelegramBot(TG_API)

logger = logging.getLogger(__name__)

async def get_all_ingredients(db: Session) -> list[Ingredient]:
    ingredients = db.query(Ingredient).all()
    return ingredients


async def get_ingredient(id: int, db: Session) -> Ingredient:
    ingredient = db.query(Ingredient).filter(Ingredient.id == id).first()
    return ingredient

@handle_errors
async def patch_ingredient(body: IngredientUpdateModel, db: Session):
    ingredient = db.query(Ingredient).filter(Ingredient.id == body.id).first()
    
    if body.using: 
        ingredient.using = body.using
    if body.stock_minimum:
        ingredient.stock_minimum = body.stock_minimum
    if body.stock_maximum:
        ingredient.stock_maximum = body.stock_maximum
    if body.min_acceptable:
        ingredient.min_acceptable = body.min_acceptable
    if body.standart_container:
        ingredient.standart_container = body.standart_container
    if body.measure:
        ingredient.measure = body.measure
    if body.provider:
        current_provider = db.query(Provider).filter(Provider.id == body.provider.id).first()
        ingredient.provider = current_provider

    db.commit()
    return ingredient


async def check_stock_balance(ingredient: Ingredient):
    keys = ("stop_list", "runing_out", "need_to_sold")
    if ingredient.amount <= ingredient.min_acceptable:
        return keys[0], ingredient.id
    elif ingredient.amount > ingredient.min_acceptable and ingredient.amount <= ingredient.stock_minimum:
        return keys[1], ingredient.id
    elif ingredient.amount > ingredient.stock_maximum:
        return keys[2], ingredient.id
    else: 
        return None


@handle_errors
async def update_ingerdients(db: Session):
    all_time_start = time.time()
    logging.basicConfig(level=logging.INFO)

    iiko_server = IikoAPIHandler()

    storage_data_time_start = time.time()

    data = await iiko_server.get_storage_balance()

    storage_data_time_end = time.time()
    logger.info(f'storage_data_time - {storage_data_time_end - storage_data_time_start}')

    stop_list_data = {
        "stop_list": [],
        "runing_out": [],
        "need_to_sold": []
    }
    cycle_time_start = time.time()
    ingredients_in_db = db.query(Ingredient).all()
    ingredients_map = {ingredient.product_id: ingredient for ingredient in ingredients_in_db}

    for obj in data:
        product_id = obj.get("product")
        ingredient = ingredients_map.get(product_id)
        if ingredient:
            # Оновлюємо дані для існуючих інгредієнтів
            ingredient.amount = obj.get("amount")
            ingredient.suma = obj.get("sum")
            stock_balance = await check_stock_balance(ingredient)
            if stock_balance:
                stop_list_data.get(stock_balance[0]).append(stock_balance[1])
        else:
            # Додаємо новий інгредієнт до списку для додавання в базу
            new_ingredient = Ingredient(
                name = obj.get("name"),
                product_id = product_id,
                amount = obj.get("amount"),
                suma = obj.get("sum"),
                using = True
            )
            db.add(new_ingredient)

    db.commit()
    cycle_time_end = time.time()
    logger.info(f'cycle_time - {cycle_time_start - cycle_time_end}')
    all_time_end = time.time()
    logger.info(f'update_ingerdients - {all_time_end - all_time_start}')
    return stop_list_data


async def calculate_order(standart_container: float, stock_maximum: float, amount: float) -> int:
    return round((stock_maximum - amount)/standart_container)


@handle_errors
async def get_order(db: Session):
    # await update_ingerdients(db)
    prov_with_ing_list = []
    providers = db.query(Provider).all()
    for provider in providers:
        provider_with_ingredients = {}
        ingredients = db.query(Ingredient).filter(
            Ingredient.provider_id == provider.id,
            Ingredient.using == True,
            Ingredient.amount < Ingredient.min_acceptable
        ).all()
        if ingredients:
            value = []
            for ingredient in ingredients:
                ing = {}
                ing["id"] = ingredient.id
                ing["name"] = ingredient.name
                ing["quantity"] = await calculate_order(ingredient.standart_container, ingredient.stock_maximum, ingredient.amount)
                value.append(ing)
            provider_with_ingredients["id"] = provider.id
            provider_with_ingredients["name"] = provider.provider_name
            provider_with_ingredients['order'] = value
        prov_with_ing_list.append(provider_with_ingredients)
    return prov_with_ing_list


@handle_errors
async def create_fake_request(chat_id: int)-> FakeBotUpdateModel:
    request = FakeBotUpdateModel(
            update_id=1234,
            message=FakeBotRequest(
                from_tg=FromTG(
                    id=chat_id,
                    is_bot=True,
                    first_name='Bot',
                    language_code='uk'
                ),
                text='Підтвердіть замовлення'
            )
        )
    return request
    


@handle_errors
async def send_order_to_provider(body: list[OrederIngByProvider], db: Session):
    for char in body:
        provider = db.query(Provider).filter(Provider.id == char.id).first()
        name = provider.salesman_name
        chat_id = provider.chat_id
        message = f"Добрий день, {name}\nЗамовлення:\n"
        for ing in char.order:
            ing_name = ing.name
            ing_quantity = ing.quantity
            msg = f"{ing_name} - {ing_quantity}"
            message += msg
        message += "\nДякую"
        await telegram_bot.send_message(chat_id, message)
        request = await create_fake_request(chat_id)
        data = await telegram_bot.make_bot_buttons(["Замовлення прийняте"], request, home=False)
        await telegram_bot.send_home(request)
        await telegram_bot.send_bot_message(data)
        await telegram_bot.send_home(request)
    return {"Message": "The order has been sent successfully"}


# @handle_errors
# async def create_ingredients(db: Session):
#     print("repository/create_ingredients")
#     iiko_server = IikoAPIHandler()
#     storage_balance = iiko_server.get_storage_balance()
#     for obj in storage_balance:
#         new_ingredient = Ingredient(
#                 name = obj.get("name"),
#                 product_id = obj.get("product"),
#                 amount = obj.get("amount"),
#                 suma = obj.get("sum"),
#                 using = True
#                     )
#         db.add(new_ingredient)
#         db.commit()
#     ingredients = db.query(Ingredient).all()
#     return ingredients
        

@handle_errors
async def delete_all(db: Session):
    ingredients = db.query(Ingredient).delete()
    db.commit()

    return {"message": "ok"}




