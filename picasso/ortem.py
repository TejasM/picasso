import json
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
    temp_url = url + str(id_member)
    try:
        Listing.objects.get(listing_name=name, scraped_url=temp_url)
    except Listing.DoesNotExist:
        continue
    r = requests.get(temp_url)
    postal = ""
    address = ""
    bio = ""
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
    tags = []
    for s in skills:
        if Tag.objects.filter(tag_name=s).count() == 0:
            t = Tag.objects.create(tag_name=s)
        else:
            t = Tag.objects.get(tag_name=s)
        tags.append(t)
    temp_url = url + str(id_member)
    l = Listing.objects.create(listing_name=name, scraped_url=temp_url)
    l.description = bio
    if l.address is None:
        try:
            add = Address.objects.create(city=cities, location=address, postal_code=postal)
            l.address = add
        except Exception as e:
            print e
    for t in tags:
        l.tags.add(t)
    l.save()


