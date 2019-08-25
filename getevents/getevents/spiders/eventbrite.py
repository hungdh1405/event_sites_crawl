# -*- coding: utf-8 -*-
import scrapy
from pathlib import Path
from datetime import datetime

def write_to_file(filePath, row):
    with open(filePath, 'a+') as f:
        f.write("{}\n".format(row))

def get_folder_path(now,country,state,city):
    path = ""

    if state != "":
        path ="{}/{}/{}/{}".format(now,country,state,city)
    else:
        path ="{}/{}/{}".format(now,country,city)

    return path

class EventbriteSpider(scrapy.Spider):
    name = 'eventbrite'
    allowed_domains = ['eventbrite.com']
    start_urls = ['https://www.eventbrite.com/directory/sitemap/']
    ONE_INDENT = "-->"
    BASE_URL = "https://www.eventbrite.com"

    def parse(self, response):
        now = datetime.today().strftime('%Y%m%d%H%M%S')
        country = ""

        for countryDom in response.css("div.panel_head2.g-grid.l-pad-all-3"):
            country = countryDom.css("h2.heading-secondary-responsive.l-mar-top-3::text").get().strip()

            if country != "Jamaica":
                continue

            if country == "Top Cities Worldwide":
                continue

            state = ""
            hasNoState = False

            for stateDom in countryDom.css("div.g-group"):
                state = stateDom.css("h3.text-heading-secondary.l-mar-top-3::text").get(default="").strip()
                if state == "":
                    hasNoState = True

                city = ""
                aTagDom = None
                aHref = ""

                for cityDom in stateDom.css("div.g-cell.g-cell-12-12.g-cell-md-4-12"):
                    city = cityDom.css("a::text").get().strip()

                    aHref = cityDom.css("a::attr(href)").get().strip().replace("/events/", "/all-events/")

                    folderPath = get_folder_path("eventbrite_" + now,country,state,city)
                    Path(folderPath).mkdir(parents=True, exist_ok=True)
                    yield scrapy.Request(
                        EventbriteSpider.BASE_URL + aHref,
                        callback=self.crawl_event,
                        cb_kwargs=dict(folderPath=folderPath)
                    )

    def crawl_event(self, response,folderPath):
        eventUrl = ""

        for event in response.css("div.search-event-card-wrapper div.eds-l-pad-all-1 aside.eds-media-card-content__image-container a.eds-media-card-content__action-link::attr(href)"):
            eventUrl = event.get()
            yield scrapy.Request(
                eventUrl,
                callback=self.crawl_event_detail,
                cb_kwargs=dict(folderPath=folderPath)
            )

        nextPage = response.css("div.paginator.eds-align--left.eds-l-mar-vert-8 div.eds-l-pad-left-4 a::attr(href)").get(default='').strip()

        if nextPage:
            yield scrapy.Request(
                        EventbriteSpider.BASE_URL + nextPage,
                        callback=self.crawl_event,
                        cb_kwargs=dict(folderPath=folderPath)
                   )

    def crawl_event_detail(self, response,folderPath):

        eventType= response.css("body::attr(id)").get()
        # eventType : event-page | page_eventview
        if eventType == "event-page":
            eventImage = response.css("div.listing-hero.listing-hero--bkg.clrfix.fx--delay-6.fx--fade-in picture::attr(content)").get()
            eventName = response.css("div.listing-hero-body h1.listing-hero-title::text").get(default='None').strip()
            eventPrice = response.css("div.js-display-price-container.listing-hero-footer.hide-small.hide-medium div.js-display-price::text").get(default='None').strip()
            eventId = response.css("body::attr(data-event-id)").get()

            eventDateTime = ""
            eventDateTime = response.css("p.listing-panel-info__details-datetime.is-truncated::text").get(default='None').strip()

            eventLocation = ""
            for addressDom in response.css("div.event-details__data")[1].css("p::text"):
                address = addressDom.get()
                if address.strip():
                    eventLocation += address.strip() + ", "

            eventDescription = response.css("div.js-xd-read-more-contents.l-mar-top-3").xpath('normalize-space()').extract_first(default='None')

            # eventID, event image, event name, event desc, ticket price, event date time, event localtion, link to buy ticket
            rowCsv = '"{}","{}","{}","{}","{}","{}","{}","{}"'.format(eventId,eventImage,eventName,eventDescription,eventPrice,eventDateTime,eventLocation,response.url)

            write_to_file(folderPath + "/data.csv",rowCsv)
        else:
            write_to_file(folderPath + "/not_event.csv",response.url)