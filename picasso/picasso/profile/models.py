from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from picasso.index.models import BaseModel, Listing, Address, Tag


class UserProfile(BaseModel):
    user = models.OneToOneField(User, related_name='profile')
    photo = models.ImageField(upload_to='avatars/', null=True)
    location = models.CharField(max_length=10000, default="")
    hobbies = models.ManyToManyField(Tag)
    phone = models.CharField(default="", max_length=100)
    teachers = models.ManyToManyField(Listing)
    nickname = models.CharField(default="", max_length=1000)
    address = models.ForeignKey(Address, default=None, null=True, blank=True)

    @property
    def get_hobbies(self):
        if self.hobbies.count() != 0:
            return ", ".join(self.hobbies.values_list('tag_name', flat=True))
        else:
            return ""


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)