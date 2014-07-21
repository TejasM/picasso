from django.contrib.gis import geos
from lxml import html
from lxml.cssselect import CSSSelector
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import requests
from picasso.index.models import Tag, Listing, Address

__author__ = 'tmehta'
emails = {"Creepy Crawlers Express Educational Presentations": "bugman@creepycrawlers.ca",
          "ANIMALS WITH WHIMZ": "whimz@whimzonline.com",
          "Animal Shows with Critter World Travelling Critters": "travellingcritters@rogers.com",
          "Glama Gal Tween Spa and Party Studio": "glamagalparty@hotmail.com",
          "Lytton Sports Camps": "info@lyttonsportscamps.com",
          "Kettleby Valley Camp and Outdoor Centre": "campisfun@kettlebyvalley.com",
          "Camp Green Acres": "",
          "Pawsitively Pets": "info@PawsitivelyPetsForKids.com",
          "Avenue Road Arts School": "contactus@avenueroadartsschool.com",
          "Bongo Productions": "bongo.tracy@gmail.com",
          "A Guide to the Best Summer Camps: OurKids.net/camp": "info@ourkids.net",
          "Ryerson University Sports Camp": "",
          "Wise Adventures": "mail@wise-adventures.ca",
          "Playtime Bowl": "strike@playtimebowl.com",
          "Sportplay": "registration@sportplay.ca",
          "TAC Sports": "info@tacsports.ca",
          "YMCA OF GREATER TORONTO SUMMER DAY CAMPS": "summer.camp@ymcagta.org",
          "Learning Jungle Summer Camp": "camps@learningjungle.com",
          "Action Potential Lab": "hello@actionpotentiallab.ca",
          "Art Gallery of Ontario": "",
          "Chef Upstairs, The": "events@thechefupstairs.com",
          "Mad Science": "toronto@madscience.on.ca",
          "National Rhythmic Gymnastics Centre": "info@nationalrg.ca",
          "Art One Academy- two locations in Richmond Hill": "info@artoneacademy.com",
          "Dazzling Divas": "sarah@dazzlingdivas.ca",
          "Active Kids Zone": "fun@activekidszone.com",
          "YOGA ROCKS kids and teens": "info@yogarocks.ca",
          "All Fired Up Paintable Ceramics": "info@afu-ceramics.com",
          "Name Labels - Iron On Name Tags": "info@namelabels.com",
          "The Circus Academy (formerly The Centre Of Gravity)": "info@thecircusacademy.ca",
          "Pedalheads Bike Camps": "info@atlantisprograms.com",
          "Conservatory of Dance and Music": "cdmdance@me.com",
          "Pris-T-giS Montessori School": "pristgismontessori@gmail.com",
          "Discovery Day Camp": "camp@tmsschool.ca",
          "Second City Camps": "akliffer@secondcity.com",
          "Evergreen's Green City Adventure Camp": "lisa@evergreen.ca",
          "Outward Bound Canada": "info@outwardbound.ca",
          "Planet Play": "info@planet-play.ca",
          "Groove School of Dance": "",
          "4Cats Arts Studio Meadowvale - Mississauga": "meadowvale@4cats.com",
          "Alpha's Discovery Club Theme Parties and Indoor Playground": "info@alphasdiscoveryclub.com",
          "Steeles West Gymnastics": "ruthy@fitforlifegroup.com",
          "Camp Kirk": "henri@campkirk.com",
          "Drama Mamas, The": "info@thedramamamas.com",
          "Just Bounce Trampoline Club Inc": "info@justbounce.ca",
          "Scouts Canada": "gtc@scouts.ca",
          "Camp Eden Camps": "info@campedenwoods.com",
          "Summer STEM Camp": "dfallowfield@pirweb.org",
          "Balls of Fun Inc.": "info@ballsoffun.ca",
          "Designher Co.": "info@designherco.com",
          "Ontario Science Centre": "recreationalprograms@ontariosciencecentre.ca",
          "Freehand School of Art": "info@freehandart.ca",
          "GTA Photography Classes": "info@gtaphotographyclasses.com",
          "RoyalCrest Academy & Camp RoyalCrest": "info@royalcrestacademy.com",
          "Camp Tamakwa": "howhow@tamakwa.com",
          "SPACE The School of Performing Arts for the Community of East York": "linette@the-space.ca",
          "Elite Basketball Camps": "info@elitecamps.com",
          "Adventure Valley Day Camp": "parties@adventurevalley.ca",
          "Clay Room, The": "contact@theclayroom.ca",
          "Camp PEAK: Pursuing Excellence Achievement & Knowledge": "mbeaver@tcet.com",
          "Pickering Museum Village": "museum@pickering.ca",
          "Petite Maison Montessori": "info@petitemaison.ca",
          "Focus Learning - Progressive Learning Centre": "info@focus-learning.ca",
          "Wanda's Creative Clay": "wanda@wandascreativeclay.com",
          "Kickboxing & Muay Thai Summer Camp": "info@tkmt.ca",
          "ViBE Dance & Fitness Studio": "info@vibestudio.ca",
          "Little Red Theatre": "littleredtheatre@yahoo.ca",
          "Camp Chabad Jewish Discovery Centre": "info@JewishMississauga.org",
          "RED Sandcastle Theatre": "redsandcastletheatre@gmail.com",
          "Chu's Martial Arts World": "chusmartialarts@gmail.com",
          "Toronto Summer Swim Camp": "bobhayes_@me.com",
          "Little Voices, Dancing Feet with Jodie Friesen": "littlevoices@sympatico.ca",
          "Design Exchange Summer Camps": "education@dx.org",
          "Humber Arboretum Centre for Urban Ecology Nature Day Camps": "arboretum@humber.ca",
          "Emily Press Labels": "info@emilypress.com",
          "Learning Disabilities Association of Toronto District": "programs@ldatd.on.ca",
          "Camp Kandalore": "",
          "Bravo Academy for the Performing Arts": "info@bravoacademy.ca",
          "Art Works Art School": "info@artworksartschool.com",
          "Arts Express": "arts.express@sympatico.ca",
          "Monet's Waterlily Garden": "lisafrasca@gmail.com",
          "Orange Dot - Studio for Moms & Growing Families": "lucy@orangedotinc.com",
          "Stuck on You - Canada": "canada@stuckonyou.biz",
          "Arm's Length Puppets": "cathylee@armslengthpuppets.com",
          "Rebellion Gallery and Art Academy": "stacey@rebelliongallery.com"}

base_url = 'http://www.helpwevegotkids.com'
url = 'http://www.helpwevegotkids.com/toronto/listings/camps-across-canada?page='
listing_selector = CSSSelector('.featured > div.cleared')
url_selector = CSSSelector('.logodiv a')
no_url_selector = CSSSelector('.nologo a')
golf = Tag.objects.get_or_create(tag_name='Summer Camps')

name_selector = CSSSelector('h3 a')
phone_selector = CSSSelector('.icons .telephone')
email_selector = CSSSelector('.email')
site_selector = CSSSelector('.icons .website')
address_selector = CSSSelector('.address a')
description_selector = CSSSelector('.listingheader + p')
counter = 0
for i in range(1, 13):
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
                                                 point=geos.fromstr(point))
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
                                       address=address, phone=phone, email=email, website=site)
            l.tags = [golf[0].id]
            l.save()