import json
import urllib2
import requests
from collections import Counter, OrderedDict
from bokeh.embed import components
from bokeh.models import (
    GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, BoxSelectTool,
    BoxZoomTool)
from bokeh.resources import CDN
from django.shortcuts import render
from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim
from models import RecentAddresses as RA, Deals as D, PageCounter as PC
from bs4 import BeautifulSoup
import re


######################################################################
#               ROUTE FUNCTIONS
######################################################################



def tagbuilder(request):
    '''
    :param request:  input will be a URL
    :return: output will be a object containing the number of tags inside the html
    '''

    uniqTags = ["None Found"]
    urltext = None
    weburl = ""
    error = None

    if (request.POST or request.GET):
        weburl = request.POST.get("weburl") if request.POST else request.GET['weburl']
        print("Extracting Info from : ", weburl)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
        try:
            req = requests.get(weburl, headers=headers)
            urltext = re.sub(r"(\n|\r)+", ' ', req.text)
            soup = BeautifulSoup(req.text, 'html.parser')
            uniqTags= dict(Counter([x.name for x in soup.find_all(True)]))
            uniqTags = OrderedDict(reversed(sorted(uniqTags.items(), key=lambda t: t[1])))

        except:
            weburl = re.sub(r"(http\:\/\/)+", '', weburl)
            error = weburl


    context = {
        "links"     : urltext,
        "uniqTags"  : uniqTags,
        "weburl"    : weburl,
        "error"     : error
    }
    return render(request, "tagbuilder.html", context)




def deals(request):
    '''
    :param request: Function to calculate the deals from 'deals.com', 'slickdeals.com', 'techbargains.net'
     The return will be to the template representing all the latest deals from these 3 websiets.
     DB Source : Models -> Postgresql & Elasticsearch which loads the deals on the fly through ETL.py
    :return:
    '''
    if request.POST:
        from ETL import Deals
        d = Deals()
        d.buildIndex()
        obj = D()
        obj.save()
    es = Elasticsearch()
    dealnews = []
    slickdeals = []
    tech = []
    lastRefreshed = D.objects.order_by('-timestamp')[0]
    try:
        res = es.search(index="deals", doc_type="dealnews",
                        body={
                            "query": {
                                "bool": {}
                            },
                            "size": 12,
                            "sort": {
                                "time": {
                                    "order": "asc"}}
                        })

        for hit in res['hits']['hits']:
            dealnews.append(hit["_source"])

        res = es.search(index="deals", doc_type="slickdeals",
                        body={
                            "query": {
                                "bool": {}
                            },
                            "size": 12,
                            "sort": {"time": {"order": "asc"}}
                        })

        for hit in res['hits']['hits']:
            slickdeals.append(hit["_source"])

        res = es.search(index="deals", doc_type="tbgs",
                        body={
                            "query": {
                                "bool": {}
                            },
                            "size": 12,
                            "sort": {"time": {"order": "asc"}}
                        })

        for hit in res['hits']['hits']:
            tech.append(hit["_source"])
            print(hit["_source"])

        context = {
            "dealnews": dealnews,
            "slickdeals": slickdeals,
            "techbargains": tech,
            "lastRefreshed": lastRefreshed
        }

    except:
        context = json.load(open("posts/static/deals.json"))
        context["ESError"] = "yes",
        context["lastRefreshed"] = lastRefreshed
        # Use this below to create a new json
        # json.dump(context, open("posts/static/deals.json",'w'))

    pageCounter = (PC.objects.filter(route='deals')[0])
    pageCounter.count += 1
    context["pageCounter"] = pageCounter
    pageCounter.save()
    return render(request, "deals.html", context)


def es(request):
    context = {
        "hi":"hello"
    }
    return render(request, "es.html", context)


def walkscore(request):
    '''
    :param request: Main logic for calculating crime rate and the vicinity map. The function takes address as an
     through the post or get api, and returns the template that contaisn the image of the criem map from
     crimereports.com and a map using bokeh on Google Maps ( using GMAP module, to plot the vicinity). The
     vicinity data comes from locu.com which when provided with a lat-long and a radius, returns a list of
     categories around that area and the radius of those each public places.
    :return:
    '''
    origimage = ''
    since = '01/01/2016'
    address = None
    script = None
    div = None
    vicinity = None
    error = None

    if (request.POST):
        address = request.POST.get("houseaddress", "")
        print("POst address", address)

    if (request.GET):
        address = request.GET['houseaddress']

    print("Address to be found is : {0}".format(address))

    if request.POST or request.GET:

        (script, div, vicinity) = showmap(address)
        print("This is vicinity: ", vicinity)
        if "categories" in vicinity:
            vicinity = vicinity["categories"]
            # vicinity is a dictionary, converting it to sorted list using itertools Sorted Unordered Dictionary
            vicinity = OrderedDict(reversed(sorted(vicinity.items(), key=lambda t: t[1])))
            print("This is vicinity : ", vicinity)
        else:
            pass

        # Selenium
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        import time

        filename = str(int(time.time())) + ".png"
        browser = webdriver.Chrome('./posts/chromedriver')
        browser.get('http://www.crimereports.com/map/index/?search=' + address)
        browser.maximize_window()
        el = browser.find_element_by_id('expand_footer')
        el.click()

        # browser.implicitly_wait(3)
        time.sleep(3)

        # import selenium.webdriver.common.action_chains.ActionChains
        import selenium.webdriver.common.action_chains as ss
        actions = ss.ActionChains(browser)

        actions.context_click(browser.find_element_by_xpath('//*[@id="crMapCanvas"]'))
        actions.perform()
        actions.context_click(browser.find_element_by_xpath('//*[@id="crMapCanvas"]'))
        actions.perform()
        time.sleep(4)

        actions.click(browser.find_element_by_id('advancedSearchNavButton'))
        actions.perform()

        time.sleep(2)

        el = browser.find_element_by_id('date-from')
        el.clear()

        try:
            if request.GET['since']:
                since = request.GET['since']
        except:
            since = '01/01/2016'
        finally:
            el.send_keys(since)

        el.send_keys(Keys.ESCAPE)
        time.sleep(2)
        btn = browser.find_element_by_class_name('crime-types-wrap')
        btn.find_element_by_class_name('btn-action').click()

        time.sleep(5)

        browser.save_screenshot('./posts/static/' + filename)
        browser.quit()

        obj = RA(address=address, imageFile=filename)
        obj.save()
        from PIL import Image
        img = Image.open('./posts/static/' + filename)

        # print("This is the size ", img.size)
        width, height = img.size  # Get dimensions

        new_img = img.crop((0, 140, width, height - 100))
        new_img.save('./posts/static/' + filename)
        # new_img.save('./posts/static/new'+filename)

        origimage = filename

    try:
        top5 = {
            "sanjose": getAddresses("sanjose"),
            "almaden": getAddresses("almaden"),
            "campbell": getAddresses("campbell"),
            "mountainview": getAddresses("mountainview")
        }
    except:
        print("Ofcourse there was an Error")
        top5 = json.load(open("posts/static/house.json"))
        error = 'yes'
        # Use this when laoding new files
        # json.dump(top5, open("posts/static/house.json",'w'))



    recentAddresses = RA.objects.order_by('-timestamp')[:10]
    pageCounter = (PC.objects.filter(route='walkscore')[0])
    pageCounter.count += 1





    context = {
        "address": address,
        "script": script,
        "div": div,
        "top5": top5,
        "origImage": origimage,
        "since": since,
        "vicinity": vicinity,
        "recentAddresses": recentAddresses,
        "ESError": error,
        "pageCounter": pageCounter
    }
    pageCounter.save()
    return render(request, "crime_walk.html", context)


######################################################################
#               UTIL FUNCTIONS FOR ROUTES
######################################################################


def showmap(add):
    '''
    :param add: Input is address that calls multiple functions to return the categories dictionary, the tag that
     contains the data in HTML format generated from the bokeh plot map and a script that goes with it.
    :return:
    '''
    script = None
    tag = None
    latlongDict = {}
    for address in [str(add)]:

        try:
            geolocator = Nominatim()
            location = geolocator.geocode(address)
            latlongDict = getVicinity(location.latitude, location.longitude)
            # html += plotHTML(location, latlongDict)
            (script, tag) = plotHTML(location, latlongDict)
            print("Function::ShowMap : Finding {0}".format(address))
        except:
            print("Function::ShowMap : WARN : Cannot find  {0}".format(address))
            pass
    return (script, tag, latlongDict)


def getVicinity(lat, long):
    '''
    When given an input of lat=long, returns the actual data consisting of a list of vicinity lat-longs within
    radius. Current default radius is 1000 meters ( around 1 Km ).
    :return:
    '''
    url = 'https://api.locu.com/v1_0/venue/search/?'
    location = "location=" + "%2C".join([str(lat), str(long)])
    radius = '&radius=1000'
    api = '&api_key=6b97e5e8438903cdb69e8563c18e324693ab984d'
    url = "".join([url, location, radius, api])

    # print("This is the URL to locu API : ", url)
    json_obj = urllib2.urlopen(url)
    decoded_data = json.load(json_obj)
    latlongDict = {"latarr": [], "longarr": [], "categories": {}}
    categories = []

    for items in decoded_data["objects"]:
        latlongDict["latarr"].append(items["lat"])
        latlongDict["longarr"].append(items["long"])
        # latlongDict["categories"].append(items["categories"])
        categories.append(items["categories"])

    categories = [item for l in categories for item in l]
    latlongDict["categories"] = dict(Counter(categories))
    print(latlongDict["categories"])
    return latlongDict


def getLatLong(address):
    '''

    :param address: Actual address to lat-long conversion happens using the geolocator module
    :return:
    '''
    geolocator = Nominatim()
    return (geolocator.geocode(address))


def plotHTML(location, latlongDict):
    '''
    :param location: given a location & a dictionary of vicinity lat-longs of categories, this function will
     calculate bokeh map seperating the main locatin ( address) and the other vicinity based on the input
     and creates a object ( script & tag html ) of the chart which is rendered on the front end.
    :param latlongDict:
    :return:
    '''
    print("Found : {0} latitudes".format(len(latlongDict["latarr"])))
    print("Found : {0} longitudes".format(len(latlongDict["longarr"])))

    map_options = GMapOptions(lat=location.latitude, lng=location.longitude, map_type="roadmap", zoom=15)
    plot = GMapPlot(
        x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="Austin"
    )
    source = ColumnDataSource(
        data=dict(
            lat=latlongDict["latarr"],
            lon=latlongDict["longarr"],
        ))
    # print([location.latitude,latlongDict["latarr"]])

    circle = Circle(x="lon", y="lat", size=10, fill_color="blue", fill_alpha=0.8, line_color=None)
    plot.add_glyph(source, circle)

    source = ColumnDataSource(
        data=dict(
            lat=[location.latitude],
            lon=[location.longitude],
        ))
    circle = Circle(x="lon", y="lat", size=15, fill_color="red", fill_alpha=0.8, line_color=None)
    plot.add_glyph(source, circle)
    plot.add_tools(PanTool(), BoxSelectTool(), BoxZoomTool())
    # return file_html(plot, CDN, "my plot")
    return (components(plot, CDN))  # Will return a (script, tag)


def getAddresses(area):
    '''
    :param area: Just a function to check the ES is functional
    :return: a list of the area to generate the boxes in the front end.
    '''
    mylist = []
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    res = es.search(index="addresses", body={"query": {"bool": {"must": [{"term": {"area": area}}]}}, "size": 5})
    print("Got %d Hits:" % res['hits']['total'])
    for hit in res['hits']['hits']:
        mylist.append(hit["_source"]["location"])
    return mylist
