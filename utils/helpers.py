import json


def read_json(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def format_price(price_str):
    nums = list(filter(lambda price: price.isdigit(), price_str))
    if not nums:
        return 0
    return int("".join(nums))