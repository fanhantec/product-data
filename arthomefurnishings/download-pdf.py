import urllib.parse
import os
import json
import hashlib

file_name = "output.txt"

try:
    os.mkdir("pdf")
    print(u"创建文件夹：", "pdf")
except OSError:
    print(u"文件夹已存在：", "pdf")

file_url_pdf = open("url_pdf_map.txt", "w")

num = 1
with open(file_name, "r") as f:
    lines = f.readlines()
    for line in lines:
        line_dict = json.loads(line)
        url = line_dict["product_url"]
        print("("+str(num)+"/"+str(len(lines))+")")
        print(u"处理url:", url)
        urlp = urllib.parse.urlparse(url)
        
        pdf_name = "pdf/" + hashlib.md5(url.encode("utf8")).hexdigest() + ".pdf"
        print(u"pdf文件名:", pdf_name)
        file_url_pdf.write(url+"\t"+pdf_name+"\n")
        if os.path.exists(pdf_name):
            print(u"文件已存在，跳过")
            continue
        #os.system("wkhtmltopdf --cookie firstpageload firstpageloadvalue "+url+" "+ pdf_name)
        num += 1
print(u"下载完成")