import re

from bs4 import BeautifulSoup
from django.contrib.gis import geos
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import requests
from picasso.index.models import Listing, Tag, Address


__author__ = 'tmehta'
base_url = 'https://members.karate-ontario.com/members/memberships.html/assoc-page/map-mapper?association_id='

tag = Tag.objects.get(tag_name='Karate', dash_version='karate')
for i in range(1, 1000):
    scraped_url = base_url + str(i)
    try:
        Listing.objects.get(scraped_url=scraped_url)
    except Listing.DoesNotExist:
        r = requests.get(scraped_url)
        if "Association is inactive" not in r.text:
            soup = BeautifulSoup(r.text)
            content = soup.select('.rightbox_content')[0].findAll(text=True)
            content = [re.sub(' +', ' ', x.replace('\n', '').strip()) for x in content if
                       x != '\n' and x != 'TEL:' and x != 'CELL:']
            description = ''
            while len(content) > 3 and (content[2] != 'Site:' or content[2] != 'Email:'):
                description += content[2]
                content.pop(2)
            if len(content) == 15:
                listing_name = content[0]
                school = content[1]
                site = content[4]
                email = content[7]
                location = content[9]
                city = content[10].split(',')[0]
                country = 'Canada'
                postal_code = content[11]
                phone = content[13].replace('Tel: ', '').replace('Cell:', '')
                try:
                    results = Geocoder.geocode(str(location + ' ' + postal_code + ' Canada'))
                    lat, lon = results[0].coordinates
                except IndexError:
                    lat, lon = 43.7, 79.4
                except GeocoderError:
                    lat, lon = 43.7, 79.4
                print lat, lon
                l = Listing.objects.create(listing_name=listing_name, scraped_url=scraped_url)
                l.description = description
                l.email = email
                l.phone = phone
                l.active = True
                if l.address is None:
                    try:
                        point = "POINT(%s %s)" % (lon, lat)
                        add = Address.objects.create(city=city, location=location, postal_code=postal_code,
                                                     point=geos.fromstr(point))
                        l.address = add
                    except Exception as e:
                        print postal_code
                else:
                    point = "POINT(%s %s)" % (lon, lat)
                    l.address.point = point
                    l.address.save()
                l.tags = [tag.id]
                l.save()
            elif len(content) == 14:
                listing_name = content[0]
                school = content[1]
                site = content[4]
                email = content[7]
                location = content[9]
                city = content[10].split(',')[0]
                country = 'Canada'
                phone = content[12].replace('Tel: ', '').replace('Cell:', '')
                try:
                    results = Geocoder.geocode(str(location + ' Canada'))
                    lat, lon = results[0].coordinates
                except IndexError:
                    lat, lon = 43.7, 79.4
                except GeocoderError:
                    lat, lon = 43.7, 79.4
                print lat, lon
                l = Listing.objects.create(listing_name=listing_name, scraped_url=scraped_url)
                l.description = description
                l.email = email
                l.phone = phone
                l.active = True
                if l.address is None:
                    try:
                        point = "POINT(%s %s)" % (lon, lat)
                        add = Address.objects.create(city=city, location=location, postal_code='',
                                                     point=geos.fromstr(point))
                        l.address = add
                    except Exception as e:
                        print ''
                else:
                    point = "POINT(%s %s)" % (lon, lat)
                    l.address.point = point
                    l.address.save()
                l.tags = [tag.id]
                l.save()
            elif len(content) == 12:
                listing_name = content[0]
                school = content[1]
                email = content[4]
                location = content[6]
                city = content[7].split(',')[0]
                country = 'Canada'
                postal_code = content[8]
                phone = content[10].replace('Tel: ', '').replace('Cell:', '')
                try:
                    results = Geocoder.geocode(str(location + ' ' + postal_code + ' Canada'))
                    lat, lon = results[0].coordinates
                except IndexError:
                    lat, lon = 43.7, 79.4
                except GeocoderError:
                    lat, lon = 43.7, 79.4
                print lat, lon
                l = Listing.objects.create(listing_name=listing_name, scraped_url=scraped_url)
                l.description = description
                l.email = email
                l.phone = phone
                l.active = True
                if l.address is None:
                    try:
                        point = "POINT(%s %s)" % (lon, lat)
                        add = Address.objects.create(city=city, location=location, postal_code=postal_code,
                                                     point=geos.fromstr(point))
                        l.address = add
                    except Exception as e:
                        print postal_code
                else:
                    point = "POINT(%s %s)" % (lon, lat)
                    l.address.point = point
                    l.address.save()
                l.tags = [tag.id]
                l.save()

            elif len(content) == 11:
                listing_name = content[0]
                school = content[1]
                email = content[4]
                location = content[6]
                city = content[7].split(',')[0]
                country = 'Canada'
                phone = content[9].replace('Tel: ', '').replace('Cell:', '')
                try:
                    results = Geocoder.geocode(str(location + ' Canada'))
                    lat, lon = results[0].coordinates
                except IndexError:
                    lat, lon = 43.7, 79.4
                except GeocoderError:
                    lat, lon = 43.7, 79.4
                print lat, lon
                l = Listing.objects.create(listing_name=listing_name, scraped_url=scraped_url)
                l.description = description
                l.email = email
                l.phone = phone
                l.active = True
                if l.address is None:
                    try:
                        point = "POINT(%s %s)" % (lon, lat)
                        add = Address.objects.create(city=city, location=location, postal_code='',
                                                     point=geos.fromstr(point))
                        l.address = add
                    except Exception as e:
                        print ''
                else:
                    point = "POINT(%s %s)" % (lon, lat)
                    l.address.point = point
                    l.address.save()
                l.tags = [tag.id]
                l.save()
            else:
                print content