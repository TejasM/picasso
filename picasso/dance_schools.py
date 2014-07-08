from django.db import DataError
from lxml import html
from lxml.cssselect import CSSSelector
import requests
from picasso.index.models import Listing, Tag, Address

__author__ = 'tmehta'
urls = ['http://www.danceontario.ca/schools?&', 'http://www.danceontario.ca/schools?&&page=1',
        'http://www.danceontario.ca/schools?&&page=2']
for url in urls:
    r = requests.get(url)
    tree = html.fromstring(r.text)
    company_name_selector = CSSSelector('.views-field-field-user-company a')
    city_selector = CSSSelector('.views-field-field-user-city .field-content')
    site_url_selector = CSSSelector('.views-field-field-web-url .field-content')
    phone_selector = CSSSelector('.views-field-field-phone .field-content')
    styles = CSSSelector('.views-field-field-user-dance-styles .field-content')

    names = [x.text for x in company_name_selector(tree)]
    city = [x.text for x in city_selector(tree)]
    phone = [x.text for x in phone_selector(tree)]
    set_of_tags = [[y.strip() for y in x.text.split(',')] for x in styles(tree) if x.text is not None]
    for n, c, p, tags in zip(names, city, phone, set_of_tags):
        django_tags = []
        p = p.split('/')[0].strip()
        p = p.split('or')[0].strip()
        p = p.split('c')[0].strip()
        c = c.strip()
        for t in tags:
            try:
                t = Tag.objects.get(tag_name=t)
            except Tag.DoesNotExist:
                t = Tag.objects.create(tag_name=t)
            django_tags.append(t.id)
        try:
            l = Listing.objects.get(listing_name=n, scraped_url=url)
        except Listing.DoesNotExist:
            try:
                l = Listing.objects.create(listing_name=n, scraped_url=url, phone=p)
            except DataError:
                print p
        l.tags = django_tags
        if l.address is None:
            if c == '':
                c = "Toronto"
            address = Address.objects.create(city=c)
            l.address = address
        l.save()