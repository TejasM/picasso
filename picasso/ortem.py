import json
from pygeocoder import Geocoder
from pygeolib import GeocoderError
from picasso.index.models import Tag, Listing, Address
import requests

__author__ = 'tmehta'
js = open('ortem.txt').read()
r = json.loads(js)
members = r['members']
names = members[0]
ids = members[1]
url = 'http://www.ormta.org/Content/Members/MemberPublicProfile.aspx?pageId=1718443&memberId='
for info, id_member in zip(names, ids):
    name = info['c1'][0]['v']
    cities = info['c4'][0]['v']
    skills = info['c2'][0]['v'].split(', ')
    active = info['c3'][0]['v'] == "Active"
    temp_url = url + str(id_member)
    # try:
    # Listing.objects.get(listing_name=name, scraped_url=temp_url)
    # continue
    # except Listing.DoesNotExist:
    #     pass
    r = requests.get(temp_url)
    postal = ""
    address = ""
    bio = ""
    email = ""
    phone = ""
    try:
        postal = r.text.split('Postal code')[1].split('</span>')[1].split('">')[2]
    except:
        pass
    try:
        address = r.text.split('Address')[1].split('</span>')[1].split('">')[2]
    except:
        pass
    try:
        bio = r.text.split('Bio')[1].split('</span>')[1].split('">')[2]
    except:
        pass
    try:
        phone = r.text.split('Phone')[1].split('</span>')[1].split('">')[2]
    except:
        pass
    try:
        email = r.text.split('e-Mail')[1].split('</span>')[1].split('">')[2].split('target=_blank>')[1].split('</a>')[0]
    except:
        pass
    tags = []
    try:
        results = Geocoder.geocode(str(address + ' ' + postal + ' Canada'))
        lat, lon = results[0].coordinates
        print lat, lon
    except IndexError:
        lat, lon = 43.7, 79.4
    except GeocoderError:
            lat, lon = 43.7, 79.4
    for s in skills:
        if Tag.objects.filter(tag_name=s).count() == 0:
            t = Tag.objects.create(tag_name=s)
        else:
            t = Tag.objects.get(tag_name=s)
        tags.append(t)
    temp_url = url + str(id_member)
    try:
        l = Listing.objects.get(listing_name=name, scraped_url=temp_url)
    except Listing.DoesNotExist:
        l = Listing.objects.create(listing_name=name, scraped_url=temp_url)
    l.description = bio
    l.email = email
    l.phone = phone
    l.active = active
    if l.address is None:
        try:
            add = Address.objects.create(city=cities, location=address, postal_code=postal, lat=lat, lon=lon)
            l.address = add
        except Exception as e:
            print postal
    else:
        l.address.lon = lon
        l.address.lat = lat
        l.address.save()
    for t in tags:
        l.tags.add(t)
    try:
        l.save()
    except:
        print phone


