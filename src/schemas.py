from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import ClassVar, Annotated
from fastapi import UploadFile, File
from src.database.models import Tag, Role
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

    class Config:
        orm_mode = True
        from_attributes = True

#############################################

class CommentResponseModel(BaseModel):
    id: int
    comment: str

    class Config:
        orm_mode = True
        from_attributes = True

############################################

class ProviderResponse(BaseModel):
    id: int
    provider_name: str
    salesman_name: str
    salesman_phone: int
    info: str

    class Config:
        orm_mode = True
        from_attributes = True


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
    provider_id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True


class ShortIngPersponseModel(BaseModel):
    name: str
    measure: str = None

    class Config:
        orm_mode = True
        from_attributes = True


class DishM2MIngredients(BaseModel):
    ingredient_id: int
    quantity: float
    ingredient: ShortIngPersponseModel

    class Config:
        orm_mode = True
        from_attributes = True



#######################################33

class PremixModel(BaseModel):
    name: str
    ingredients: list[IngredientModel]
    description: str
    

class PremixM2MIngredients(BaseModel):
    ingredient_id: int
    quantity: float
    ingredient: ShortIngPersponseModel

    class Config:
        orm_mode = True
        from_attributes = True




class PremixResponseModel(BaseModel):
    id: int
    name: str
    premix_ingredients: list[PremixM2MIngredients]
    description: str

    class Config:
        orm_mode = True
        from_attributes = True


class PremixToDishModel(BaseModel):
    id: int
    name: str
    quantity: float

    class Config:
        orm_mode = True
        from_attributes = True


class DishM2MPremixes(BaseModel):
    premix_id: int
    quantity: float
    premix: PremixResponseModel
    
    class Config:
        orm_mode = True
        from_attributes = True

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
    dish_premixes: Optional[list[DishM2MPremixes]] = Any
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

    class Config:
        orm_mode = True
        from_attributes = True



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

    class Config:
        orm_mode = True
        from_attributes = True

#########################################
    


########################################3

class AddPhotoModel(BaseModel):
    photo: Annotated[bytes, File()]

class HelloResponsemodel(BaseModel):
    BotMessage: str


class UploadTextModel(BaseModel):
    message: str

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
    id: Optional[int]
    name: Optional[str]
    quantity: Optional[int]

class OrederIngByProvider(BaseModel):
    id: Optional[int]
    name: Optional[str]
    order: Optional[list[IngOrderModel]]


###############################################3

class AvailableDishesModel(BaseModel):
    dishes: Optional[list[DishResponseModel]]

class StopListModel(BaseModel):
    stop_list: Optional[list[DishResponseModel]]
    runing_out: Optional[list[DishResponseModel]]
    need_to_sold: Optional[list[DishResponseModel]]
    
    class Config:
        orm_mode = True
        from_attributes = True



################################################

class UserResponseModel(BaseModel):
    id: int
    name: str
    username: str
    first_name: str
    last_name: str
    email: str
    information: str
    phone: str = None
    role: Role = Field()
    forward_provider_message: bool

    class Config:
        orm_mode = True
        from_attributes = True

class UserModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    role: Role = Field()
    information: str
    password: str
    refresh_token: str
    
    class Config:
        orm_mode = True
        from_attributes = True


class UserUpdateModel(BaseModel):
    id: int
    name: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    banned: Optional[bool] = None
    information: Optional[str] = None
    forward_provider_message: Optional[bool] = None

    class Config:
        orm_mode = True
        from_attributes = True


class UserRegistrationBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=16)

    class Config:
        orm_mode = True
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str







    