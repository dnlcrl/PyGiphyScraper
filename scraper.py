#!/usr/bin/env python
# encoding: utf-8

from selenium import webdriver
import urllib
import json
from time import sleep

# MACROS
SERVER = 'server'
URL = 'url'
FILE = 'file'
FILE_DIRECTORY = 'gifs/'


class Services(object):

    """docstring for Services"""

    GIPHY = 'giphy'
    keys = [GIPHY]
    home_pages = {GIPHY: 'http://giphy.com/search/'}
    mp4_pages = {
        GIPHY: {SERVER: 'http://media', URL: '.giphy.com/media/', FILE: '/giphy.mp4'}}


class Scraper(object):

    """docstring for Scraper"""

    def __init__(self, service, verbose, limit, tags):
        super(Scraper, self).__init__()
        self.service = service
        if service not in Services.keys:
            print 'error: service ' + service + ' not in service list'
            print 'service list: ' + str(Services.keys())
            return
        self.url = Services.home_pages[service] + 'xnxnxnxnxnxn'
        self.search_url = Services.home_pages[service] + ''.join([x + '-' for x in tags])[:-1]
        self.tags = tags
        self.verbose = verbose
        self.limit = limit
        self.number_of_scraped_gifs = 0
        self.gif_ids = {}
        self.directory = FILE_DIRECTORY + ''.join([t + ' ' for t in tags][:-1])
        self.json_file = self.directory + '_gifs.json'
        profile = webdriver.FirefoxProfile()
        profile.set_preference("webdriver.load.strategy", "unstable")
        #profile.set_preference("general.useragent.override","Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/41.0.2272.58 Mobile/12B440 Safari/600.1.4")
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(10)
        self.log('Driver Initialized')
        try:
            self.log('connecting to the url: ' + self.url)
            #self.driver.get(self.url)
            # import pdb; pdb.set_trace()
            # self.driver.find_element_by_id('autoplay-toggle').click()
            self.driver.get(self.search_url)
            self.log('Success!')
        except Exception, e:
            print 'url error, check the following Exception'
            raise e

    def log(self, s):
        if self.verbose:
            print s

    def search_box(self):
        self.log('Searching the search box')
        if self.service == Services.GIPHY:
            return self.driver.find_element_by_id('search-box')

    def search_button(self):
        self.log('Searching the search button')
        if self.service == Services.GIPHY:
            return self.driver.find_element_by_id('search-button')

    def retrieve_number_of_gifs(self):
        import pdb; pdb.set_trace()
        self.log('Searching for the number of gifs')
        if self.service == Services.GIPHY:
            return self.driver.find_element_by_class_name('found-count').text.split(' ')[0]

    def search_tags(self):
        #self.log('Locating Elements')
        #self.search_box().send_keys(''.join([t + ' ' for t in self.tags])[:-1])
        #self.log(
        #    'Launching the GIF search, current Url: ' + self.driver.current_url)
        #self.search_button().click()
        self.log('Query executed, current Url: ' + self.driver.current_url)
        gif_number = self.retrieve_number_of_gifs()
        self.log('Total GIFs found: ' + gif_number)
        if gif_number < self.limit:
            self.limit = gif_number

    def save_gif_ids(self):
        with open(self.json_file, 'w') as outfile:
                json.dump(self.gif_ids, outfile)

    def search_gifs(self):
        gif_ids = []
        if self.service == Services.GIPHY:
            while self.number_of_scraped_gifs < self.limit:
                self.log('Locating Links')
                gif_links = [l for l in self.driver.find_elements_by_class_name('gif-link')]
                self.log('Building dict struct')
                gif_ids = {e.get_attribute('data-id'): [x.replace(' ', '') for x in e.find_element_by_tag_name(
                    'figcaption').text.split(',')] for e, e in zip(gif_links, gif_links)}
                self.log(str(gif_ids))
                new_ids = set(self.gif_ids) - set(gif_ids.keys())
                self.log('Yielding new_ids')
                yield new_ids
                self.gif_ids.update(gif_ids)
                self.save_gif_ids()
                self.driver.execute_script(
                    'window.scrollTo(0,document.body.scrollHeight);')
                sleep(1.5)

    def retrieve_file(self, gif_id):
        if self.service == Services.GIPHY:
            servers = ['', '0', '1', '2', '3', '4']
            url_struct = Services.mp4_pages[Services.GIPHY]
            for s in servers:
                try:
                    file_url = url_struct[
                        SERVER] + s + + url_struct[URL] + gif_id + url_struct[FILE]
                    self.log('Saving GIF nr: ' + str(self.number_of_scraped_gifs))
                    urllib.urlretrieve(
                        file_url, self.directory + gif_id + '.' + url_struct[FILE].split('.')[-1])
                    break
                except Exception, e:
                    print e

    def loop(self):
        for gif_ids in self.search_gifs():
            for gif_id in gif_ids:
                self.retrieve_file(gif_id)
                self.number_of_scraped_gifs += 1

    def run(self):
        self.search_tags()
        self.loop()

        # download gifs
