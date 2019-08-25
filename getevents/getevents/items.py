# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GeteventsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    event_id = scrapy.Field()
    image = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    datetime = scrapy.Field()
    location = scrapy.Field()
