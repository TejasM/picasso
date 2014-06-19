import json
from picasso.index.models import Tag, Listing

__author__ = 'tmehta'
js = open('ortem.txt').read()
r = json.loads(js)
members = r['members']
names = members[0]
ids = members[1]
url = 'http://www.ormta.org/Content/Members/MemberPublicProfile.aspx?pageId=1718443&memberId='
for info, id_member in zip(names, ids):
    name = info['c1'][0]['v']
    address = info['c4'][0]['v']
    skills = info['c2'][0]['v'].split(', ')
    tags = []
    for s in skills:
        if Tag.objects.filter(tag_name=s).count() == 0:
            t = Tag.objects.create(tag_name=s)
        else:
            t = Tag.objects.get(tag_name=s)
        tags.append(t)
    temp_url = url + str(id_member)
    l = Listing.objects.create(listing_name=name, scraped_url=temp_url)
    for t in tags:
        l.tags.add(t)
    l.save()


