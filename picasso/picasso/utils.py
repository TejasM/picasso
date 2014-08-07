import logging
import random
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.template.loader import get_template
from picasso.index.models import Listing

__author__ = 'tmehta'

logger = logging.getLogger(__name__)


def send_claim_email(listing):
    if listing.email != '':
        try:
            l = Listing.objects.get(hash_key=listing.hash_key)
        except Exception as e:
            print e
            return "Fail"
        emails = ['emails/claim_email.html', 'emails/claim_email_2.html']
        choice = random.choice(emails)
        logger.debug('Listing claim sending email to : ' + listing.email + ' with ' + choice)
        t = get_template(choice)
        context = RequestContext({'method': 'GET'}, {'listing': listing})
        content = t.render(context)
        msg = EmailMessage('Picasso - Claim your Business', content, 'contact@findpicasso.com', [listing.email])
        msg.content_subtype = "html"
        msg.send()
        return "Success"
    return "Fail"


def decodeHtmlentities(string):
    import re

    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")

    def substitute_entity(match):
        from htmlentitydefs import name2codepoint as n2cp

        ent = match.group(2)
        if match.group(1) == "#":
            return unichr(int(ent))
        else:
            cp = n2cp.get(ent)

            if cp:
                return unichr(cp)
            else:
                return match.group()

    return entity_re.subn(substitute_entity, string)[0]