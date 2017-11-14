import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import datetime
import json
import queue
import threading
import shutil
import sys

class Product():
    # 初始化
    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Mobile Safari/537.36",\
                        "Host":"www.altuntaskilim.com.tr",\
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",\
                        "Connection":"keep-alive",\
                        "Referer":"http://www.altuntaskilim.com.tr/our-products"}
        
        self.brand_name = "Altuntas Hali Kilim"
        self.brand_alia = "altuntaskilim"
        self.base_url = "http://www.altuntaskilim.com.tr/our-products"

        # 连接MongoDB
        client = MongoClient()
        # 选择数据库
        db = client["product"]
        # 存储一个brand下所有product的url
        self.brand_collection = db["brand"]
        
        # 选择集合
        self.product_collection = db[self.brand_alia]
        self.product_name = ''
        self.product_url = ''
        self.product_tag = ''
        self.product_img_urls = []

        # 创建目录
        try:
            os.mkdir(self.brand_name)
            print(u'创建文件夹：', self.brand_name)
        except OSError:
            print(u'文件夹已存在：', self.brand_name)

        # 代理
        self.proxyOn = False
        self.proxy = ""
        if self.proxyOn:
            self.proxy = self.get_proxy()

    def get_proxy(self):
        # 这里填写无忧代理IP提供的API订单号（请到用户中心获取）
        order = "0e177a11bad27220bb2c9b750d57d69a"; 
        # 获取IP的API接口
        apiUrl = "http://api.ip.data5u.com/dynamic/get.html?order=" + order;

        proxy = requests.get(apiUrl).text.strip("\n")

        print(u"获取代理IP：", proxy)

        return proxy
    
    def timing_get_proxy(self):
        self.proxy = self.get_proxy()
        print(u"获取代理IP：", self.proxy)
        self.timer = threading.Timer(60, self.timing_get_proxy)
        self.timer.start()
    
    def clear_db_brand(self):
        print(u"删除brand所有的url")
        self.brand_collection.remove({"brand_alia": self.brand_alia})
    def clear_db_product(self):
        print(u"删除所有product的信息")
        self.product_collection.remove()
    def clear_db(self):
        self.clear_db_brand()
        self.clear_db_product()

    def export_db_brand(self):
        print(u"导出brand")
        brand_products = self.brand_collection.find_one({"brand_alia": self.brand_alia})
        output = ""
        output += brand_products["brand_alia"] + '\n'
        output += str(brand_products["flag"]) + '\n'
        output += str(brand_products["brand_product_urls"]) + '\n'
        output += str(brand_products["created_time"]) + '\n'
        if "last_page" in brand_products:
            output += str(brand_products["last_page"]) + '\n'
        with open("output." + self.brand_alia + ".brand.txt", "w") as f:
            f.write(output)
    
    def export_db_product_urls(self):
        print(u"导出所有商品URL信息")
        brand_products = self.brand_collection.find_one({"brand_alia": self.brand_alia})
        output = ""
        if brand_products:
            for url in brand_products["brand_product_urls"]:
                product_tag = {"product_url": url, "brand_name": self.brand_name, "httpUrl": url}
                output += json.dumps(product_tag) + "\n"
        with open("output." + self.brand_alia + ".product.urls.txt", "w") as f:
            f.write(output)
    
    def export_db_product(self):
        print(u"导出所有product信息")
        output = ""
        products = []
        for product in self.product_collection.find():
            product_tag = json.loads(product["product_tag"])
            if product_tag["product_url"] in products:
                continue
            products.append(product_tag["product_url"])
            output += product["product_tag"] + "\n"          
            
        print(len(products))
        print(len(list(set(products))))
        with open("output." + self.brand_alia + ".product.txt", "w") as f:
            f.write(output)
    
    def download_img(self):
        print(u"下载所有product图片")
        num = 1
        products = []
        for product in self.product_collection.find():
            product_tag = json.loads(product["product_tag"])
            # 去重用
            if product_tag["product_url"] in products:
                continue
            products.append(product_tag["product_url"])
            print(u"开始处理商品：", product_tag["product_url"], "(" + str(num) + "/" + str(2395) + ")")
            # 图片存储路径
            thumbnail = product_tag["thumbnail"]
            img_urls = product["product_img_urls"]
            # 创建图片存储目录
            try:
                os.makedirs(thumbnail)
                print(u'创建图片存储目录：', thumbnail)
            except OSError:
                print(u'图片存储目录已存在：', thumbnail)
            # 保存图片
            print(u"一共图片数目：", len(img_urls))
            if self.proxyOn:
                self.proxy = self.get_proxy()
            for img_url in img_urls:
                img_name = self.get_img_name(img_url)
                self.save_img(img_url, img_name, thumbnail)
            print(u"图片下载成功")
            num += 1

    # 返回网页Response
    def request(self, url):
        content=""
        try:
            if self.proxyOn:
                content = requests.get(url, headers=self.headers, proxies={'http':'http://' + self.proxy})
            else:
                content = requests.get(url, headers=self.headers)
        except Exception:
            print(u"异常：",url)
            return None
        return content

    # 保存图片
    def save_img(self, img_url, img_name, img_path):
        print(u"图片URL：", img_url)
        if os.path.exists(os.path.join(img_path, img_name)):
            print(u"图片已存在，跳过")
            return
        img = self.request(img_url)
        with open(os.path.join(img_path, img_name), "wb") as f:
            f.write(img.content)

    # 保存到数据库
    def save_db(self):
        post = {
            "product_name": self.product_name,
            "product_url": self.product_url,
            "product_tag": json.dumps(self.product_tag),
            "product_img_urls": self.product_img_urls,
            "created_time": datetime.datetime.now()
        }
        self.product_collection.save(post)
        print(u"商品信息入库成功")
    
    # 提取并保存商品信息
    def save_product(self, product_url):
        print(u"开始处理商品：", product_url)
        request_html = self.request(product_url)
        if request_html == None:
            print(u"跳过")
            return
        product_html = request_html.text
        product_html = BeautifulSoup(product_html, "lxml")

        self.product_url = product_url
        # 分析产品的tag信息并保存
        self.product_name, self.product_tag, product_img_path = self.get_product_tag(product_url, product_html)
        print(u"商品tag信息已获取")
        # 分析产品的img信息并保存
        self.product_img_urls = self.get_product_img_urls(product_html)
        #print(u"保存商品图片")
        # 创建图片存储目录
        try:
            os.makedirs(product_img_path)
            print(u'创建图片存储目录：', product_img_path)
        except OSError:
            print(u'图片存储目录已存在：', product_img_path)
        # 保存图片
        print(u"一共图片数目：", len(self.product_img_urls))
        for img_url in self.product_img_urls:
            img_name = self.get_img_name(img_url)
            #self.save_img(img_url, img_name, product_img_path)
        print(u"图片下载成功")

        # 保存数据库
        self.save_db()

    # 从product_html中获取product_tag
    def get_product_tag(self, product_url, product_html):
        product_tag = {}

        # sku
        sku = product_html.find("div", id="gkMainbody").find("h1").get_text().strip()
        print("sku:", sku)

        # production_name
        production_name = ""        
        # size
        size = ""
        # description
        description = ""      

        group = ""
        thumbnail = self.brand_name + "/" + sku
        sizeName = ""

        # 人工判断字段
        category_option_1 = ""
        category_code = []
        room_code = []
        color_code = []
        style_code = []
        material_code = []
        # brand_name
        brand_name = self.brand_name
        # material
        material = ""        
        # volume
        volume = ""
        # weight
        weight = ""
        # httpUrl
        httpUrl = product_url

        product_tag["product_url"] = product_url
        product_tag["sku"] = sku
        product_tag["group"] = group
        product_tag["production_name"] = production_name
        product_tag["size"] = size
        product_tag["sizeName"] = sizeName
        product_tag["thumbnail"] = thumbnail
        product_tag["category_option_1"] = category_option_1
        product_tag["category_code"] = category_code
        product_tag["room_code"] = room_code
        product_tag["color_code"] = color_code
        product_tag["style_code"] = style_code
        product_tag["material_code"] = material_code
        product_tag["brand_name"] = brand_name
        product_tag["description"] = description
        product_tag["material"] = material
        product_tag["volume"] = volume
        product_tag["weight"] = weight
        product_tag["httpUrl"] = httpUrl         

        return production_name ,product_tag, thumbnail

    # 从product_html中获取product_img_urls
    def get_product_img_urls(self, product_html):
        img_urls = []
        img_src = product_html.find("div", id="gkMainbody").find("div", class_="main-image").find("img").get("src")
        img_url = "http://www.altuntaskilim.com.tr" + img_src
        img_urls.append(img_url)
        return img_urls

    # 从img_url中获取img_name
    def get_img_name(self, img_url):
        img_name = img_url.split('/')[-1]
        return img_name

    # 从product_html中获取图片存储路径
    def get_product_img_path(self, product_html):
        product_img_path = ""

        sku_list = product_html.find("span", class_="sku").get_text().split(",")
        sku = sku_list[0]
        product_img_path = sku
        return product_img_path

    # 从html中获取到product_urls
    def get_product_urls(self, html):
        print(u"开始获取所有产品的URL...")
        product_urls = []

        html = BeautifulSoup(html, "lxml")
        
        brand_products = self.brand_collection.find_one({"brand_alia": self.brand_alia})
        last_page = 0
        # 获取数据库中的记录，用于跳过
        if brand_products:
            product_urls = brand_products["brand_product_urls"]
            last_page = brand_products["last_page"]
        
        # 分页处理
        max_page = "78"
        print(u"总页数：", max_page)
        for page in range(0, int(max_page)):
            page_url = "http://www.altuntaskilim.com.tr/our-products?start=" + str(page*48)
            if page == 0:
                page_url = "http://www.altuntaskilim.com.tr/our-products?limitstart=0"
            
            print(u"分页URL:", page_url, "(", str(page) + "/" + max_page + ")")

            if page < last_page:
                print(u"该页处理完，跳过")
                continue
            if self.proxyOn:
                self.proxy = self.get_proxy()
            
            page_html = self.request(page_url).text
            page_html = BeautifulSoup(page_html, "lxml")
            tag_div_rows = page_html.find("div", class_="browse-view").find_all("div", class_="row")
            for div_row in tag_div_rows:
                tag_div_spacers = div_row.find_all("div", class_="spacer")
                for div_spacer in tag_div_spacers:
                    product_url = "http://www.altuntaskilim.com.tr" + div_spacer.find("a", rel="vm-additional-images").get("href")
                    print(u"产品URL：", product_url)
                    if product_url not in product_urls:
                        product_urls.append(product_url)
            
            self.brand_collection.remove({"brand_alia": self.brand_alia})
            self.brand_collection.save({"brand_alia": self.brand_alia, "flag": False, "brand_product_urls": product_urls, "last_page": page, "created_time": datetime.datetime.now()})
            print(u"保存分页数据")

        print(u"获取所有产品的URL成功")
        return product_urls

    def start(self):
        print(u"开始处理网站：", self.base_url)
        product_urls = []
        # 先从数据库中查找是否已经获取到了所有product的url
        brand_products = self.brand_collection.find_one({"brand_alia": self.brand_alia})
        if brand_products:
            print(u"数据库中存在所有产品的URL，直接获取")
            product_urls = brand_products["brand_product_urls"]
        else:
            print(u"解析网站信息")
            html = self.request(self.base_url).text
            product_urls = self.get_product_urls(html)
            self.brand_collection.save({"brand_alia": self.brand_alia, "flag": True, "brand_product_urls": product_urls, "created_time": datetime.datetime.now()})
            print(u"所有产品的URL入库成功")

        num = 1
        for product_url in product_urls:
            # 从数据库中查找是否商品信息已获取
            if self.product_collection.find_one({"product_url": product_url}):
                print(u"商品信息已入库，跳过：", product_url)
            else:
                if num < 1000:
                    print(u"跳过")
                    num += 1
                    continue
                if num >= 4000:
                    print(u"已经完成")
                    break
                print("(" + str(num) + "/" + str(len(product_urls)) + ")", sep="")
                if self.proxyOn and num%2==0:
                    self.proxy = self.get_proxy()
                self.save_product(product_url)
            num += 1

if __name__ == "__main__":
    log = open("console.log", "w+")
    #sys.stdout=log
    #sys.stderr=log 
    product = Product()
    # 开始爬取数据
    #product.start()

    # 清除数据库信息
    #product.clear_db()
    #product.clear_db_brand()
    product.clear_db_product()

    # 导出数据库信息
    #product.export_db_brand()
    #product.export_db_product_urls()
    product.export_db_product()

    # 下载图片
    #product.download_img()
