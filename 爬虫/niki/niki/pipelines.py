# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NikiPipeline:
    def process_item(self, item, spider):
        with open('shop.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return item
