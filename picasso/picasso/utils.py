import logging
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.template.loader import get_template

__author__ = 'tmehta'

logger = logging.getLogger(__name__)


def send_claim_email(listing):
    logger.debug('Listing claim sending email to : ' + listing.email)
    if listing.email != '':
        t = get_template('emails/claim_email.html')
        context = {'listing': listing}
        content = t.render(context)
        msg = EmailMessage('Picasso - Message for your Business', content, 'contact@findpicasso.com', [listing.email])
        msg.content_subtype = "html"
        msg.send()
        return "Success"
    return "Fail"