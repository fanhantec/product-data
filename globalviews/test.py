import json

file_pdf = open("filepdf", "r")

file_pdf_dict = {}

for line in file_pdf.readlines():
    url, pdf = line.strip().split("\t")
    file_pdf_dict[url] = "https://voice.fanhantech.com/html1/pdf/" + pdf

file_src = open("output.globalviews.brand.txt", "r")
file_dest = open("output.txt", "w+")

for line in file_src.readlines():
    product = json.loads(line)
    url = product["product_url"]
    product["product_url"] = file_pdf_dict[url]

    product["sku"] = ""
    product["group"] = ""
    product["production_name"] = ""
    product["size"] = ""
    product["sizeName"] = ""
    product["thumbnail"] = ""
    product["category_option_1"] = ""
    product["category_code"] = []
    product["room_code"] = []
    product["color_code"] = []
    product["style_code"] = []
    product["material_code"] = []
    product["description"] = ""
    product["material"] = ""
    product["volume"] = ""
    product["weight"] = ""    

    file_dest.write(json.dumps(product) + "\n")
    