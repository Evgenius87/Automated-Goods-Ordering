
# import hashlib
# import json
# import functools
# import logging
# import requests
# from datetime import datetime
# from os.path import join, dirname
# from dotenv import load_dotenv

# from src.conf.config import settings


# logger = logging.getLogger(__name__)

# def handle_errors(method):
#     """
#     The handle_errors function is a decorator that wraps the decorated function in a try/except block.
#     If an exception occurs, it logs the error and returns None.
    
#     :param method: Pass the method to be decorated
#     :return: A wrapper function
#     :doc-author: Trelent
#     """
#     @functools.wraps(method)
#     def wrapper(self, *args, **kwargs):
#         """
#         The wrapper function is a decorator that wraps the original function.
#             It prints out the name of the function and its arguments, then calls
#             it. If an exception occurs, it logs that exception to a file.
        
#         :param self: Allow an instance of the class to call its own methods
#         :param *args: Send a non-keyworded variable length argument list to the function
#         :param **kwargs: Pass a variable number of keyword arguments to the function
#         :return: The result of the method or an error message if something goes wrong
#         :doc-author: Trelent
#         """
#         logging.basicConfig(level=logging.INFO)
#         try:
#             return method(self, *args, **kwargs)
#         except Exception as e:
#             logger.info(f"Something wrong wit method '{method.__name__}': {e}")
#     return wrapper



# class IikoAPIHandler:
#     def __init__(self):
#         """
#         The __init__ function is called when the class is instantiated.
#         It sets up the instance variables that will be used by other methods in the class.
        
        
#         :param self: Represent the instance of the class
#         :return: None by default, but you can return other values
#         :doc-author: Trelent
#         """
#         self.__login = settings.resto_login
#         self.__password = settings.resto_password
#         self.sha1_encoding = hashlib.sha1()
#         self._auth_url = settings.resto_auth_url
#         self._storage_url = settings.resto_storage_url
#         self._nomenclature_url = settings.resto_nomenclature_url
#         self._products_url = settings.resto_products_url
#         self.__token = self.get_authorization_token()
#         self.timestamp = self.get_current_timestamp()


#     @handle_errors
#     def get_authorization_token(self) -> list[dict]:
#         """
#         The get_authorization_token function is used to get the authorization token from the server.
#                 The function returns a list of dictionaries with keys: 'token' and 'user_id'.
                     
#         :param self: Access the attributes and methods of a class
#         :return: A list of dictionaries
#         :doc-author: Trelent
#         """
#         self.sha1_encoding.update(self.__password.encode('utf-8'))  
#         password_encoded = self.sha1_encoding.hexdigest()
#         data = {"login": self.__login, "pass": password_encoded}
#         response = requests.post(url=self._auth_url, data=data)
#         return response.text

#     @handle_errors
#     def get_nomenclature(self) -> list[dict]:
#         """
#         The get_nomenclature function returns a list of dictionaries containing the nomenclature for each item in the database.
#             The function takes no arguments and returns a list of dictionaries.
        
#         :param self: Reference the object itself
#         :return: A list of dictionaries, each dictionary representing a nomenclature
#         :doc-author: Trelent
#         """
#         full_url = f"{self._nomenclature_url}?key={self.__token}"
#         response = requests.get(url=full_url)
#         return response.text

#     @handle_errors
#     def get_products(self) -> list[dict]:
#         """
#         The get_products function returns a list of dictionaries containing the product information.

#         :param self: Refer to the current instance of the class
#         :return: A list of dictionaries
#         :doc-author: Trelent
#         """
#         full_url = f"{self._products_url}?key={self.__token}&timestamp={self.timestamp}"
#         response = requests.get(full_url)
#         return response.text

#     @handle_errors
#     def get_current_timestamp(self) -> str:
#         """
#         The get_current_timestamp function returns a string representing the current UTC time.
#             The format of the returned string is: YYYY-MM-DDTHH:MM:SS
        
#         :param self: Represent the instance of the class
#         :return: A string that represents the current timestamp
#         :doc-author: Trelent
#         """
#         current_timestamp = datetime.utcnow()
#         timestamp_str = current_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
#         return timestamp_str
    
#     @handle_errors
#     def preparation_data(self, data: list[dict]) -> list[dict]:
#         ingredient_dict = {}
#         for ingredient in data:
#             ingredient_id = ingredient["product"]
#             if ingredient_id in ingredient_dict:
#                 ingredient_dict[ingredient_id]['amount'] += ingredient['amount']
#                 ingredient_dict[ingredient_id]['sum'] += ingredient['sum']
#                 continue
#             ingredient_dict[ingredient['product']] = ingredient
#         updated_ingredients = list(ingredient_dict.values())
#         return updated_ingredients


#     @handle_errors
#     def get_storage_balance(self) -> list[dict]:
#         """
#         The get_storage_balance function returns a list of dictionaries containing the product id, name and balance.
#             The function uses the get_products and get_nomenclature functions to retrieve data from two different endpoints.
#             It then iterates through both lists of dictionaries to find matching ids between products and nomenclature.
#             If there is a match, it adds the item's name as an additional key-value pair in the product dictionary.
        
#         :param self: Represent the instance of the class
#         :return: A list of dictionaries
#         :doc-author: Trelent
#         """
#         print("servise/iico")
        
#         products = json.loads(self.get_products())
#         nomenclature = json.loads(self.get_nomenclature())
#         products = self.preparation_data(products)

#         for product in products:
#             prod_id = product.get("product")
#             for item in nomenclature:
#                 item_id = item.get("id")
#                 item_name = item.get("name")

#                 if prod_id == item_id:
#                     product["name"] = item_name
                
#         return products


# # iiko_server = IikoAPIHandler()
# # storage_balance = iiko_server.get_storage_balance()
# # # print(storage_balance)

# # for obj in storage_balance:
# #     if "віскі" in obj.get("name"):
# #         print(obj)

import aiohttp
import hashlib
import json
from datetime import datetime
from fastapi import HTTPException
from src.conf.config import settings

class IikoAPIHandler:
    def __init__(self):
        """
        Ініціалізація класу IikoAPIHandler
        """
        self.__login = settings.resto_login
        self.__password = settings.resto_password
        self.sha1_encoding = hashlib.sha1()
        self._auth_url = settings.resto_auth_url
        self._storage_url = settings.resto_storage_url
        self._nomenclature_url = settings.resto_nomenclature_url
        self._products_url = settings.resto_products_url
        self.__token = None
        self.timestamp = self.get_current_timestamp()

    async def get_authorization_token(self) -> str:
        """
        Асинхронне отримання токена авторизації від сервера
        """
        self.sha1_encoding.update(self.__password.encode('utf-8'))
        password_encoded = self.sha1_encoding.hexdigest()
        data = {"login": self.__login, "pass": password_encoded}

        async with aiohttp.ClientSession() as session:
            async with session.post(self._auth_url, data=data) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Authorization failed")
                # result = await response.json()
                # self.__token = result.get("token")
                # return self.__token
            
                result = await response.text()
                self.__token = result
                # print(f"iiko_token = {result}")
                return self.__token

    async def get_nomenclature(self) -> list[dict]:
        """
        Асинхронне отримання номенклатури
        """
        if not self.__token:
            await self.get_authorization_token()

        full_url = f"{self._nomenclature_url}?key={self.__token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch nomenclature")
                return await response.json()

    async def get_products(self) -> list[dict]:
        """
        Асинхронне отримання продуктів
        """
        if not self.__token:
            await self.get_authorization_token()

        full_url = f"{self._products_url}?key={self.__token}&timestamp={self.timestamp}"
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch products")
                return await response.json()

    def get_current_timestamp(self) -> str:
        """
        Отримання поточного часу у форматі UTC для використання в запитах
        """
        current_timestamp = datetime.utcnow()
        timestamp_str = current_timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        return timestamp_str

    def preparation_data(self, data: list[dict]) -> list[dict]:
        """
        Обробка даних, об'єднання однакових продуктів за ідентифікатором
        """
        ingredient_dict = {}
        for ingredient in data:
            ingredient_id = ingredient["product"]
            if ingredient_id in ingredient_dict:
                ingredient_dict[ingredient_id]['amount'] += ingredient['amount']
                ingredient_dict[ingredient_id]['sum'] += ingredient['sum']
            else:
                ingredient_dict[ingredient_id] = ingredient
        return list(ingredient_dict.values())

    async def get_storage_balance(self) -> list[dict]:
        """
        Асинхронне отримання балансу продуктів зі складу та номенклатури, 
        зіставлення продуктів із номенклатурою.
        """
        if not self.__token:
            await self.get_authorization_token()

        # Паралельні запити до продуктів та номенклатури
        async with aiohttp.ClientSession() as session:
            products_task = session.get(f"{self._products_url}?key={self.__token}&timestamp={self.timestamp}")
            nomenclature_task = session.get(f"{self._nomenclature_url}?key={self.__token}")
            
            async with products_task as products_response, nomenclature_task as nomenclature_response:
                if products_response.status != 200 or nomenclature_response.status != 200:
                    raise HTTPException(status_code=500, detail="Failed to fetch data from Iiko")

                products = await products_response.json()
                nomenclature = await nomenclature_response.json()

        # Обробка продуктів
        products = self.preparation_data(products)
        
        # Створення словника для номенклатури для швидкого доступу
        nomenclature_dict = {item["id"]: item["name"] for item in nomenclature}

        # Додавання назв продуктів до кожного продукту
        for product in products:
            prod_id = product.get("product")
            product["name"] = nomenclature_dict.get(prod_id)

        return products