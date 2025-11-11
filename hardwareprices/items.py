# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HardwarepricesItem(scrapy.Item):
    # define the fields for your item here like:
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    link = scrapy.Field()
    store = scrapy.Field()
