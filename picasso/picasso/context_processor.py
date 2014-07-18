from django.db.models import Q, Count
from picasso.index.models import Tag, Listing

__author__ = 'tmehta'


def get_current_tags(request):
    full_tags = Tag.objects.annotate(num_listings=Count('listings')).filter(parent_tag=None, visible=True).order_by(
        'num_listings')
    all_tags = Tag.objects.annotate(num_listings=Count('listings')).filter(visible=True).order_by('num_listings')
    all_tags = [str(x.tag_name) for x in all_tags]
    count = Listing.objects.count()
    tags = [str(x.tag_name) for x in full_tags]
    return {'tags': tags, 'full_tags': full_tags, 'all_tags': all_tags, 'number_of_listings': count}