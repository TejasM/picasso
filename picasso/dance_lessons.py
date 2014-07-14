# coding=utf-8
from django.contrib.gis import geos
from lxml import html
from lxml.cssselect import CSSSelector
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import requests
from picasso.index.models import Tag, Listing, Address

__author__ = 'tmehta'
emails = {"In The Mix": "jackie@inthemixprogram.com",
          "National Rhythmic Gymnastics Centre": "info@nationalrg.ca",
          "Rugcutterz Danz Artz": "stephanie@rugcutterz.com",
          "Martha Hicks School of Ballet": "office@mhsb.ca",
          "Conservatory of Dance and Music": "cdmdance@me.com",
          "School of CCDT – Canadian Contemporary Dance Theatre": "schoolofccdt@ccdt.org",
          "SPACE The School of Performing Arts for the Community of East York": "linette@the-space.ca",
          "STARting Pointe Productions ltd. - Jump STARters": "info@startingpointeproductions.com",
          "ViBE Dance & Fitness Studio": "info@vibestudio.ca",
          "Groove School of Dance": "",
          "Swansea School of Dance": "info@swanseaschoolofdance.com",
          "Royal Academy Of Dance": "info@radcanada.org", }

base_url = 'http://www.helpwevegotkids.com'
url = 'http://www.helpwevegotkids.com/toronto/listings/after-school-programs-and-weekend-activities/dance-lessons?page='
listing_selector = CSSSelector('.featured > div.cleared')
url_selector = CSSSelector('.logodiv a')
no_url_selector = CSSSelector('.nologo a')
tag = Tag.objects.get_or_create(tag_name='Dance')
name_selector = CSSSelector('h3 a')
phone_selector = CSSSelector('.icons .telephone')
email_selector = CSSSelector('.email')
site_selector = CSSSelector('.icons .website')
address_selector = CSSSelector('.address a')
description_selector = CSSSelector('.listingheader + p')
counter = 0
for i in range(1, 6):
    r = requests.get(url + str(i))
    tree = html.fromstring(r.text)
    listings = listing_selector(tree)
    for listing in listings:
        try:
            scraped_url = base_url + url_selector(listing)[0].attrib['href']
        except IndexError:
            scraped_url = base_url + no_url_selector(listing)[0].attrib['href']
        r = requests.get(scraped_url)
        listing = html.fromstring(r.text)
        name = name_selector(listing)[0].text.strip()
        phone = phone_selector(listing)
        if phone:
            phone = phone[0].attrib['telephone']
        else:
            phone = ''
        if name in emails:
            email = emails[name]
        else:
            email = ''
        site = site_selector(listing)
        if site:
            site = site[0].attrib['href']
        else:
            site = ''
        address = address_selector(listing)
        if address:
            temp = address[0].text.split(',')
            if temp:
                if temp > 1:
                    location = temp[0]
                    postal_code = temp[-1]
                else:
                    location = ''
                    postal_code = temp[0]
                try:
                    results = Geocoder.geocode(str(location + ' ' + postal_code + ' Canada'))
                    lat, lon = results[0].coordinates
                except IndexError:
                    lat, lon = 43.7, 79.4
                except GeocoderError:
                    lat, lon = 43.7, 79.4
                point = "POINT(%s %s)" % (lon, lat)
                address = Address.objects.create(location=location, postal_code=postal_code,
                                                 point=geos.fromstr(point), website=site)
            else:
                address = None
        else:
            address = None
        description = description_selector(listing)
        if description:
            description = description[0].text
        else:
            description = ''
        if not description:
            description = ''
        if Listing.objects.filter(scraped_url=scraped_url).count() == 0:
            l = Listing.objects.create(listing_name=name, description=description, scraped_url=scraped_url,
                                       address=address, phone=phone, email=email)
            l.tags = [tag[0].id]
            l.save()