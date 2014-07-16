from django.db.models import Q
from picasso.index.models import Tag, Listing

__author__ = 'tmehta'


def get_current_tags(request):
    full_tags = Tag.objects.filter(parent_tag=None).order_by('?')
    all_tags = Tag.objects.all().order_by('?')
    all_tags = [str(x) for x in all_tags.values_list('tag_name', flat=True)]
    count = Listing.objects.count()
    tags = [str(x) for x in full_tags.values_list('tag_name', flat=True)]
    return {'tags': tags, 'full_tags': full_tags, 'all_tags': all_tags, 'number_of_listings': count}