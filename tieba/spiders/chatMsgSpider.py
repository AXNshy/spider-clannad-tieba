#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import scrapy
import mysql.connector
from mysql.connector.errors import DatabaseError
# import sys
# sys.path.append("..")
from tieba.items import PostItem


class chatMsgSpider(scrapy.Spider):
    name = 'chatMsg'
    allowed_domains = ['baidu.com']
    start_urls = [
        'https://tieba.baidu.com/f?kw=clannad&ie=utf-8'
    ]
    def __init__(self):
        self.currentIndex = 0
        self.data = []

    def setUrl(self, url):
        self.start_urls.append(url)

    def parse(self, response):
        # for sel in response.xpath("//ul[@id='thread_list']"):
        for sel in response.xpath("//li[contains(@class,'j_thread_list')]"):
            # li = sel.xpath("//li[@class='j_thread_list']")
            item = PostItem()
            try:
                item['title'] = self.extractInfo(sel.xpath(".//div[contains(@class,'threadlist_abs')]/text()").extract())
                item['date'] = self.extractInfo(sel.xpath(".//span[contains(@class,'is_show_create_time')]/text()").extract())
                item['url'] = self.extractInfo(sel.xpath(".//div[contains(@class,'threadlist_title pull_left j_th_tit')]").xpath("a/@href").extract())
                item['author'] = self.extractInfo(sel.xpath(".//span[contains(@class,'tb_icon_author')]/@title").extract())
                print(item['title'], item['date'], item['url'], item['author'])
                self.data.append(item)
                # self.saveToDb(item)
            except IndexError:
                continue
        self.currentIndex = self.currentIndex+50
        if self.currentIndex > 1000:
            self.saveToDb(self.data)
            return 
        nexturl = 'https://tieba.baidu.com/f?kw=clannad&ie=utf-8&pn='+str(self.currentIndex)    
        yield self.make_requests_from_url(nexturl)

    
    def extractInfo(self,raw):
        if len(raw) == 0:
            return ""
        else:
            return raw[0].strip()

    def saveToDb(self,raw):
        
        conn = mysql.connector.connect(user='root', password='root', database='tieba', charset='utf8mb4')
        cursor = conn.cursor()
        # for post in raw:
        try:
            for post in raw:
                cursor.execute('insert into tiebademo1(title,date,url,author) values (%s,%s,%s,%s)', [post['title'], post['date'], post['url'], post['author']])
            conn.commit()
            cursor.close()
            conn.close()
        except DatabaseError as e:
            print(e.msg)
            print(post)

        
        # //*[@id="frs_list_pager"]/a[10]   