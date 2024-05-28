import json
from pprint import pprint

# with open("ing_response.json", "wb") as fp:
# ingredients = json.load("ing_response.json")

# print(ingredients)

with open("ing_response.json", "r", encoding='UTF-8') as json_data:
    data = json_data.read()
    data = json.loads(data)

for ingredient in data:
    if "Чед" in ingredient["name"]:
        print(ingredient)