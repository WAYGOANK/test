import json
import re
import time

import scrapy


class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["www.nike.com.cn", "api.nike.com.cn"]
    number = 50
    header = {
        # 'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': 'Linux',
        'nike-api-caller-id': 'com.nike.commerce.nikedotcom.web',
        # 'referer': 'https://www.nike.com.cn/'
    }
    start_urls = [f"https://{allowed_domains[1]}/cic/browse/v2?queryid=products&anonymousId=B0rNhAK47ozmGPJUtKOgA&country=cn&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(CN)%26filter%3Dlanguage(zh-Hans)%26filter%3DemployeePrice(true)%26anchor%3D0%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{number}&language=zh-Hans&localizedRangeStr=%7BlowestPrice%7D%20%E2%80%94%20%7BhighestPrice%7D"]

    def parse(self, response):
        json_data = json.loads(response.text)
        for index, item in enumerate(json_data.get('data').get('products').get('products')):
            groupid = re.findall("-(.*?)/", item['url'])[0].split('-')[-1]
            url = "https://" + self.allowed_domains[0] + item['url'].lstrip('{countryLang}')
            yield scrapy.Request(callback=self.parse_detail, url = url, meta={'groupid': groupid})

    def parse_detail(self, response):
        html = response.text
        groupid = response.meta['groupid']
        data = dict()
        data['title'] = response.xpath('//*[@id="pdp_product_title"]/text()').extract()[0]
        try:
            data['price'] = response.xpath('//div[@class="mb4-sm mb8-lg"]/div[@id="price-container"]/span/text()').extract()[0]
            data['color'] = response.xpath('//*[@id="product-description-container"]/ul/li[1]/text()').extract()[-1]
            data['sku'] = response.xpath('//*[@id="product-description-container"]/ul/li[2]/text()').extract()[-1]
            data['details'] = response.xpath('//*[@id="product-description-container"]/p/text()').extract()[0]
        except:
            data['color'] = re.search("显示颜色： (.*?)\"", html).group(1)
            data['price'] = re.search("¥([0-9,]*)", html).group()
            data['sku'] = re.search("款式： ([A-Za-z0-9-]*)", html).group(1)
        # data['img_urls'] = json.loads(response.xpath('//*[@id="__NEXT_DATA__"]/text()').extract()[0]).get('props').get('pageProps').get('selectedProduct').get('contentImages')
        img_url = list()
        try:
            for i in json.loads(response.xpath('//*[@id="__NEXT_DATA__"]/text()').extract()[0]).get('props').get('pageProps').get('selectedProduct').get('contentImages'):
                if i.get('cardType') == 'video':
                    continue
                img_url.append(i.get('properties').get('squarish').get('url'))
            data['img_urls'] = img_url
        except:
            data['img_urls'] = []
        url = f"https://{self.allowed_domains[1]}/discover/product_details_availability/v1/marketplace/CN/language/zh-Hans/consumerChannelId/d9a5bc42-4b9c-4976-858a-f159cf99c647/groupKey/{groupid}"
        yield scrapy.Request(url = url, callback=self.get_size, meta={'data': data}, headers=self.header)

    def get_size(self, response):
        data = response.meta['data']
        siez_list = json.loads(response.text).get('sizes')
        siezs = list()
        # print(siez_list)
        for item in siez_list:
            if item.get('availability').get('isAvailable'):
                siezs.append(item.get('localizedLabel'))
        data['siezs'] = siezs
        # print(data)
        yield data