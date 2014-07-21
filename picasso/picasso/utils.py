import logging
import random
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.template.loader import get_template

__author__ = 'tmehta'

logger = logging.getLogger(__name__)


def send_claim_email(listing):
    logger.debug('Listing claim sending email to : ' + listing.email)
    if listing.email != '':
        emails = ['emails/claim_email.html', 'emails/claim_email_2.html']
        choice = random.choice(emails)
        logger.debug('Listing claim sending email to : ' + listing.email + ' with ' + choice)
        t = get_template(choice)
        context = RequestContext({}, {'listing': listing})
        content = t.render(context)
        msg = EmailMessage('Picasso - Claim your Business', content, 'contact@findpicasso.com', [listing.email])
        msg.content_subtype = "html"
        msg.send()
        return "Success"
    return "Fail"