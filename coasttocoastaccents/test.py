import requests
from bs4 import BeautifulSoup

headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Mobile Safari/537.36"}
url = "http://www.coasttocoastaccents.com/p-4839-end-table.aspx?EID=145&EN=Category"

#r = requests.get(url,headers=headers)

html = "<a></a>"

html = BeautifulSoup(html, "lxml")

description = html.find("a")

print(type(description))
print(len(list(description.children)))

print(description.name)

print(description.next)