import json
import re
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import requests
# from picasso.index.models import Tag
from picasso.index.models import Address, Listing, Tag

__author__ = 'tmehta'

url = 'http://www.yellowpages.ca/ajax/search/music+teachers/Toronto%2C+ON?sType=si&sort=rel&pg=1&' + \
      'skipNonPaids=56&trGeo=43.797452066539165,-79.15031040820315&blGeo=43.55112164714018,-79.6419485917969'

base_url = 'http://www.yellowpages.ca/bus/'
city = 'Toronto'


def extract_cats(p):
    try:
        p_s = p.split('Products and Services</h3>')[1].split('</span>')[0].replace('<span>', '')
    except IndexError:
        return []
    p_s = p_s.split("'>")[1:]
    cats = []
    for line in p_s:
        cats.append(line.split('</li>')[0])
    return cats


def extract_phone(p):
    try:
        phone = p.split('class="phone"')[1].split('<span >')[1].split('</span>')[0]
    except IndexError:
        phone = ''
    return phone


r = requests.get(url)
listings = json.loads(r.text)['features']
for l in listings:
    name = l['properties']['name']
    scraped_url = base_url + str(l['properties']['id']) + '.html'
    try:
        lst = Listing.objects.get(scraped_url=scraped_url)
        page = requests.get(scraped_url).text
        try:
            location = page.split('itemprop="streetAddress">')[1].split('</span>')[0]
        except IndexError:
            location = ''
        try:
            postalCode = page.split('itemprop="postalCode">')[1].split('</span>')[0]
        except IndexError:
            postalCode = ''
        lat = l["geometry"]["coordinates"][0]
        lon = l["geometry"]["coordinates"][1]
        point = "POINT(%s %s)" % (lon, lat)
        lst.address.point = point
        lst.save()
    except Listing.DoesNotExist:
        active = True
        place = 'Sch'
        email = ''
        page = requests.get(scraped_url).text
        categories = extract_cats(page)
        tags = []
        for cat in categories:
            t = Tag.objects.get_or_create(tag_name=cat)
        phone_number = extract_phone(page)
        try:
            location = page.split('itemprop="streetAddress">')[1].split('</span>')[0]
        except IndexError:
            location = ''
        try:
            postalCode = page.split('itemprop="postalCode">')[1].split('</span>')[0]
        except IndexError:
            postalCode = ''
        try:
            description = page.split('itemprop="description">')[1].split('</article>')[0].split('<a href')[0].replace(
                '<span', '').replace('</span>', '')
        except IndexError:
            description = ''
        lat = l["geometry"]["coordinates"][0]
        lon = l["geometry"]["coordinates"][1]
        point = "POINT(%s %s)" % (lon, lat)
        add = Address.objects.create(location=location, postal_code=postalCode, city=city, point=point)
        lst = Listing.objects.create(address=add, listing_name=name, scraped_url=scraped_url, description=description,
                                   phone=phone_number)
        for t in tags:
            lst.tags.add(t)
        lst.save()



