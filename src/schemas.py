from datetime import datetime
from pydantic import BaseModel, Field
from typing import ClassVar, Annotated
from fastapi import UploadFile, File
from src.database.models import Tag
from typing import Optional, Any, Union



class FromTG(BaseModel):
    chat_id: int = Field(alias='id') 
    is_bot: bool 
    first_name: str 
    last_name: str = None
    username: str = None
    language_code: str 


class FromTGBot(BaseModel):
    chat_id: int = Field(alias='id') 
    is_bot: bool 
    first_name: str 
    username: str = None
   


class ReplyMessage(BaseModel):
    message_id: int = None
    from_tg: FromTGBot = Field(alias='from')
    chat: dict = None
    date: int = None
    text: str = None


class BotMessage(BaseModel):
    message_id: Optional[int] = None
    from_tg: FromTG = Field(alias='from')
    chat: Optional[dict] = None
    date: Optional[int] = None
    text: Optional[str] = None
    reply_to_message: Optional[ReplyMessage] = None


class FakeBotRequest(BaseModel):
    message_id: Optional[int] = None
    from_tg: FromTG
    chat: Optional[dict] = None
    date: Optional[int] = None
    text: Optional[str] = None
    reply_to_message: Optional[ReplyMessage] = None

class FakeBotUpdateModel(BaseModel):
    update_id: Optional[int]
    message:FakeBotRequest = None

class BotUpdateModel(BaseModel):
    update_id: Optional[int]
    message:BotMessage = None


class ReplyKeyboardMarkup(BaseModel):
    keyboard: list


class KeyboardButton(BaseModel):
    text: str


##############################################
    
class TagResponseModel(BaseModel):
    id: int
    name_tag: str

#############################################

class CommentResponseModel(BaseModel):
    id: int
    comment: str

############################################

class ProviderResponse(BaseModel):
    id: int
    provider_name: str
    salesman_name: str
    salesman_phone: int
    info: str


class ProviderModel(BaseModel):
    id: int



#############################################
class IngredientModel(BaseModel):
    id: int
    name: str
    quantity: float


class IngredientUpdateModel(BaseModel):
    id: int
    stock_minimum: Optional[float] = None
    min_acceptable: Optional[float] = None
    stock_maximum: Optional[float] = None
    standart_container: Optional[float] = None
    measure: Optional[str] = None
    using: Optional[bool] = None
    provider: Optional[ProviderModel] = None



class IngredientResponseModel(BaseModel):
    id: int
    name: str = None
    amount: float = None
    suma: float = None
    stock_minimum: float = None
    min_acceptable: float = None
    stock_maximum: float = None
    standart_container: float = None
    measure: str = None
    using: bool = None
    provider_id: int = None


class ShortIngPersponseModel(BaseModel):
    name: str
    measure: str = None


class DishM2MIngredients(BaseModel):
    ingredient_id: int
    quantity: float
    ingredient: ShortIngPersponseModel



#######################################33

class PremixModel(BaseModel):
    name: str
    ingredients: list[IngredientModel]
    description: str


class PremixM2MIngredients(BaseModel):
    ingredient_id: int
    quantity: float
    ingredient: ShortIngPersponseModel




class PremixResponseModel(BaseModel):
    id: int
    name: str
    premix_ingredients: list[PremixM2MIngredients]
    description: str

class PremixToDishModel(BaseModel):
    id: int
    name: str
    quantity: float


class DishM2MPremixes(BaseModel):
    premix_id: int
    quantity: float
    premix: PremixResponseModel

###########################################3


class DishModel(BaseModel):
    dish_name: str
    description: Optional[str] = None
    ingredients: list[IngredientModel]
    premixes: Optional[list[PremixToDishModel]] = None
    tags: Optional[list[str]] = None
    category: str 
    price: int = None


class DishResponseModel(BaseModel):
    id: int
    image_url: Any
    image_public_id: Any
    dish_name: str
    description: Any
    dish_ingredients: list[DishM2MIngredients]
    dish_premixes: list[DishM2MPremixes] = Any
    comments: list[CommentResponseModel]
    tags: list[TagResponseModel] = Any
    stop_list: Any
    runing_out: Any
    need_to_sold: Any
    price: int
    category_name: str = None
    category_id: int = None
    created_at: datetime
    updated_at: Optional[datetime] = Any


class UpdateDishModel(BaseModel):
    id: int
    dish_name: Optional[str]
    description: Optional[str] = None
    comment: Optional[str] =None
    ingredients: Optional[list[IngredientModel]]
    premixes: Optional[list[PremixToDishModel]] = None
    tags: Optional[list[str]] = None
    category: Optional[str]
    price: Optional[int] = None


#################################33########

class OkResponseModel(BaseModel):
    message: str


#########################################33


class GetChildRequest(BaseModel):
    name: str


#########################################

class CategoryHomeModel(BaseModel):
    name: str
    


class CategoryModel(BaseModel):
    name: str
    parent: str = None


class CategoryResponseModel(BaseModel):
    id: int
    name: str
    parent_id: Union[int, None]
    child: bool
    dishes: bool

#########################################
    


########################################3

class AddPhotoModel(BaseModel):
    photo: Annotated[bytes, File()]

class HelloResponsemodel(BaseModel):
    BotMessage: str


class UploadTextModel(BaseModel):
    message: str
    
#########################################

# class CommentDeleteResponse(BaseModel):
#     id: int = 1
#     comment: str = 'My comment'

#     class Config:
#         orm_mode = True


# class CommentResponse(BaseModel):
#     id: int = 1
#     comment: str
#     username: UserDb
    

#     class Config:
#         orm_mode = True


# class CommentModel(BaseModel):
#     comment: str = Field(min_length=1, max_length=255)
#     image_id: int = Field(1, gt=0)


# class CommentModelUpdate(BaseModel):
#     comment: str = Field(min_length=1, max_length=255)
#     comment_id: int 

class CommentModel(BaseModel):
    comment: str
    user_id: int
    dish_id: int

class CommentResponeModel(BaseModel):
    id: int
    comment: str
    user_id: int
    dish_id: int

################################################
    
class IngOrderModel(BaseModel):
    id: int
    name: str
    quantity: int

class OrederIngByProvider(BaseModel):
    id: int
    name: str
    order: list[IngOrderModel]


################################################

class UsersResponseModel(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    information: str
    role: str
    forward_provider_message: bool

class UserModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    # role: str
    information: str
    password: str
    refresh_token: str


class UserResponseModel(BaseModel):
    id: int
    # name =Column(String(150), nullable=True)
    username: str = None
    first_name: str = None
    last_name: str = None
    phone: str = None
    email: str = None
    # created_at: str = None
    refresh_token: str = None
    banned: bool = None
    information: str = None
    forward_provider_message: bool = None


    