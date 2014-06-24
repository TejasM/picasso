import json
import requests

__author__ = 'tmehta'

url = 'http://www.yellowpages.ca/ajax/search/music+teachers/Toronto%2C+ON?sType=si&sort=rel&pg=1&' + \
      'skipNonPaids=56&trGeo=43.797452066539165,-79.15031040820315&blGeo=43.55112164714018,-79.6419485917969'

base_url = 'http://www.yellowpages.ca/bus/'
city = 'Toronto'

r = requests.get(url)
listings = json.loads(r.text)['listings']
for l in listings:
    name = l['name']
    page = requests.get(base_url + str(l['id']) + '.html').text


