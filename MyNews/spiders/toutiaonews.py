# -*- coding: utf-8 -*-
from ..headers import toutiaoheader
import json
import time
from scrapy_redis.spiders import RedisSpider
from MyNews.items import NewsItem
from scrapy import Request

class ToutiaoNewsSpider(RedisSpider):
    """Spider that reads urls from redis queue (sinanews:start_urls)."""

    name = 'toutiaonews'
    redis_key = 'toutiaonews:start_urls'
    tag_list = ['tech','sports','finance','entertainment']
    sum = 0

    cookies = {'tt_webid': '75308733723'}

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('toutiao.com', 'toutiao.com')
        self.allowed_domains = filter(None, domain.split(','))
        super(ToutiaoNewsSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # 每次爬400页,可自行设置
        for i in range(4000):
            for tag in self.tag_list:
                url = 'https://www.toutiao.com/api/pc/feed/?category=news_'+str(tag)+'&utm_source=' \
                      'toutiao&widen=1&max_behot_time=0&max_behot_time_tmp=0&tadrequire=true' \
                      '&as=A125AA5DDC88F50&cp=5ADC589F85308E1&_signature=uK7jowAA4n8SgaMj0J7VIbiu47'
                yield Request(url, callback=self.parsebody, headers=toutiaoheader, cookies=self.cookies, meta={'tag':tag}, dont_filter=True)

    def parsebody(self,response):
        newsjson = json.loads(response.text)
        try:
            newslist = newsjson['data']
            global newslist
        except:
            pass

        for news in newslist:
            key_list = []
            meta = response.meta
            id = news['item_id']
            item = NewsItem()
            for key in news:
                key_list.append(key)
            if 'abstract' in key_list:
                item['body'] = news['abstract']
                item['tag'] = meta['tag']
                item['title'] = news['title']
                item['url'] = 'https://www.toutiao.com/a'+str(id)
                item['pubtime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(news['behot_time']))
                item['refer'] = '今日头条'
                self.sum +=1
                print(self.sum)
                print('%%%%%%%%%%%%%%%%%%%%%%%%')
                yield item