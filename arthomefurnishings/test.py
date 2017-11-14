import json

product_tag = {}

brand_name = "Art Classics"

f = open("output.txt", "w+")

with open("src", "r") as src:
    for line in src.readlines():
        url, sku, name = line.strip().split(";")
        url = url.strip()
        sku = sku.strip()
        name = name.strip()

        product_tag["product_url"] = url
        product_tag["sku"] = sku
        product_tag["group"] = ""
        product_tag["production_name"] = name
        product_tag["size"] = ""
        product_tag["sizeName"] = ""
        product_tag["thumbnail"] = brand_name + "/" + sku
        product_tag["category_option_1"] = ""
        product_tag["category_code"] = []
        product_tag["room_code"] = []
        product_tag["color_code"] = []
        product_tag["style_code"] = []
        product_tag["material_code"] = []
        product_tag["brand_name"] = brand_name
        product_tag["description"] = ""
        product_tag["material"] = ""
        product_tag["volume"] = ""
        product_tag["weight"] = ""
        product_tag["httpUrl"] = url

        f.write(json.dumps(product_tag) + "\n")