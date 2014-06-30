from picasso.index.models import Tag

__author__ = 'tmehta'


def get_current_tags(request):
    tags = [str(x) for x in Tag.objects.all().values_list('tag_name', flat=True)]
    return {'tags': tags}