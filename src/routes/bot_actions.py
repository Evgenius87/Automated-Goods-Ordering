from pprint import pprint

from dotenv import load_dotenv

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from src.database.db_connection import get_db
from src.schemas import BotUpdateModel, OkResponseModel
from src.bot_request_handler.bot_request_handler import bot_request_handler_chain
from src.bot_request_handler.bot_request_handler import providers_bot_request_handler_chain
from src.repository.bot_contents import delete_message


router = APIRouter(prefix='/bot_actions', tags=["Bot"])

# load_dotenv()
# TG_API = os.getenv("BOT_TOKEN")


@router.post('/webhook/to_users', response_model=OkResponseModel)
async def root(obj: BotUpdateModel, db: Session = Depends(get_db)):
    await delete_message(obj)
    bot_handler_chain = await bot_request_handler_chain()
    response = await bot_handler_chain.handle_request(obj, db)
    return {'message': 'ok'}


@router.post('/webhook/to_providers', response_model=OkResponseModel)
async def root(obj: BotUpdateModel, db: Session = Depends(get_db)):
    bot_handler_chain = await providers_bot_request_handler_chain()
    response = await bot_handler_chain.handle_request(obj, db)
    return {'message': 'ok'}
    


