import re
import time

import requests
from geopy.geocoders import Nominatim
from pyes import *


class Deals:
    def __init__(self):
        self.conn = ES("http://localhost:9200")
        self.index = 'deals'

    def slickdeal(self):
        url = 'http://slickdeals.net/?&utm_source=slickdeals_com&utm_medium=redirect&utm_campaign=redirect'
        print("Extracting Info from : ", url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
        req = requests.get(url, headers=headers)
        reg = '''<div class="imageContainer">
                          <img src="(.*?)" alt="" title="(.*?)">
                      </div>'''
        reggroups = re.findall(reg, req.text)
        for i in reggroups:
            dealText = i[1]
            dealImage = i[0]
            indexType = "slickdeals"
            self.conn.index({"time": int(time.time()), "dealText": dealText, "dealImage": dealImage}, "deals",
                            indexType)

    def dealnews(self):
        url = 'http://dealnews.com/'
        print("Extracting Info from : ", url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
        req = requests.get(url, headers=headers)
        reg = '''class=" lazy-img"
            alt="(?P<data>.*?)"
            title="(.*?)"
            border="0"
            style="(.*?)"
            src="http://s2.dlnws.com/images/spacer.png"
data-src="(?P<image>.*?)"'''
        reggroups = re.findall(reg, req.text.encode('utf-8'))
        for i in reggroups:
            dealText = i[0]
            dealImage = i[3]
            self.conn.index({"time": int(time.time()), "dealText": dealText, "dealImage": dealImage}, "deals",
                            "dealnews")

    def buildIndex(self):
        self.reIndex()
        self.dealnews()
        self.slickdeal()
        return ("Everything upto Date !!")

    def reIndex(self):
        print("Rebuilding Index ")
        if self.index:
            try:
                self.conn.indices.delete_index(self.index)
                self.conn.indices.create_index(self.index)
            except:
                self.conn.indices.create_index(self.index)
        else:
            return ("Index TYPE not defined Possible options : 'deals'")


class RealEstate:
    def __init__(self):
        self.conn = ES("http://localhost:9200")
        self.index = 'addresses'

    def reIndex(self):
        if self.index:
            try:
                self.conn.indices.delete_index(self.index)
                self.conn.indices.create_index(self.index)
            except:
                self.conn.indices.create_index(self.index)
        else:
            return ("Index TYPE not defined Possible options : 'deals, addresses'")

    def getCurrentData(self):
        self.getAlmaden()
        self.getCampbell()
        self.getSanJose()
        self.getMountainView()

    def getMountainView(self):
        addressList = []
        # url = 'http://search.exclusivesanjosehomes.com/i/san-jose-homes-for-sale?start='+str(i)+ '&per=10'
        # req = requests.get(url)
        # reggroups = re.findall(r'<img alt="(.*?)" src="',req.text)
        url = 'http://www.realtor.com/realestateandhomes-search/Mountain-View_CA'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
        req = requests.get(url, headers=headers)
        reggroups = re.findall(r'<span class="listing-street-address" itemprop="streetAddress">(.*?)</span>', req.text)

        for address in reggroups:
            address += ", Mountain View, CA"
            print("Checking Address : ", address)
            try:
                geolocator = Nominatim()
                location = geolocator.geocode(address)
                if (location):
                    addressList.append(address)
            except:
                print("Function::ShowMap : WARN : Cannot find  {0}".format(address))
                pass

        # Sometimes they seem to block the greping of data, hence the hard coded list.
        if (len(addressList) < 1):
            addressList = '''2433 Laura Ln
            77 Mercy St
            1602 Morgan St
            128 Ada Ave
            609 Charmain Cir
            717 Alice Ave
            49 Showers Dr
            1100 Carlos Privada
            1465 San Marcos Cir
            428 Baywood Ct
            49 Showers Dr
            857 Sycamore Loop
            723 Sonia Way
            391 Foxborough Dr
            1857 Peacock Ave'''.split("\n")

            addressList = [eachaddress + ", Mountain View, CA" for eachaddress in addressList]

        for address in addressList:
            print(address)
            self.conn.index({"location": address, "area": "mountainview"}, "addresses", "map")

    def getSanJose(self):
        geolocator = Nominatim()
        url = 'http://search.exclusivesanjosehomes.com/i/san-jose-homes-for-sale'
        req = requests.get(url)
        reggroups = re.findall(r'<img alt="(.*?)" src="', req.text)
        for address in reggroups:
            location = ()
            print("'" + address + "'")
            try:
                # Checking if we get Longitude and Latitudes
                location = geolocator.geocode(address)
                print(location.latitude, location.longitude)
                if (location):
                    self.conn.index({"location": address, "area": "sanjose"}, "addresses", "map")
            except:
                # If not them move on.
                pass

    def getCampbell(self):
        geolocator = Nominatim()
        url = 'http://search.exclusivesanjosehomes.com/i/campbell-homes-for-sale'
        req = requests.get(url)
        reggroups = re.findall(r'<img alt="(.*?)" src="', req.text)
        for address in reggroups:
            location = ()
            print("'" + address + "'")
            try:
                # Checking if we get Longitude and Latitudes
                location = geolocator.geocode(address)
                print(location.latitude, location.longitude)
                if (location):
                    self.conn.index({"location": address, "area": "campbell"}, "addresses", "map")
            except:
                # If not them move on.
                pass

    def getAlmaden(self):
        geolocator = Nominatim()
        url = 'http://search.exclusivesanjosehomes.com/i/almaden-valley-homes-for-sale'
        req = requests.get(url)
        reggroups = re.findall(r'<img alt="(.*?)" src="', req.text)
        for address in reggroups:
            location = ()
            print("'" + address + "'")
            try:
                # Checking if we get Longitude and Latitudes
                location = geolocator.geocode(address)
                print(location.latitude, location.longitude)
                if (location):
                    self.conn.index({"location": address, "area": "almaden"}, "addresses", "map")
            except:
                # If not them move on.
                pass


def checkESConnection(index=None, doc_type=None):
    '''
    :param index: [ addresses, deals]
    :param doc_type: [ map, dealnews, slickdeals, tbgs]
    :return:
    '''
    conn = ES("http://localhost:9200")
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    res = es.search(index=index, doc_type=doc_type,
                    body={"query": {"bool": {"must": [{"term": {"area": "almaden"}}]}}, "size": 5})
    print("Got %d Hits:" % res['hits']['total'])
    for hit in res['hits']['hits']:
        print(hit["_source"]["location"])
