import json

l = [
    {
        "name": "xxx",
        "id": 123,
        "quantity": 0.1
    },
    {
        "name": "www",
        "id": 124,
        "quantity": 0.3
    }
]

str_l = str(l)

decode_l = list(str_l)

print(decode_l)