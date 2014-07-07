from lxml import html
from lxml.cssselect import CSSSelector
import requests
import nltk


__author__ = 'tmehta'
base_url = 'http://www.kijiji.ca/'
piano_url = 'http://www.kijiji.ca/b-music-lessons/gta-greater-toronto-area/piano-lessons/page-1/k0c86l1700272'


r = requests.get(piano_url)

tree = html.fromstring(r.text)
ad_selector = CSSSelector('table.regular-ad')

ads = [x.attrib['data-vip-url'] for x in ad_selector(tree)]
listing_name_selector = CSSSelector('h1')
description_selector = CSSSelector('h1')
for ad in ads:
    ad = requests.get(base_url + ad).text
    tree = html.fromstring(ad)
    name = listing_name_selector(tree)
    print name[0].text


