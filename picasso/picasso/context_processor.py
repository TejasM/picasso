from picasso.index.models import Tag

__author__ = 'tmehta'


def get_current_tags(request):
    full_tags = Tag.objects.all().order_by('?')
    tags = [str(x) for x in full_tags.values_list('tag_name', flat=True)]
    return {'tags': tags, 'full_tags': full_tags}