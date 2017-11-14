import json
import requests

headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Mobile Safari/537.36"}

file_name = "A-Office.txt"

url="https://euro.style/products/00522BLK/Alpha-Office-Chair-in-Black-with-Polished-Aluminum-Base"

r = requests.get(url, headers=headers)

print(r.text)