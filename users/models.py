from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver

from registration.signals import user_activated

from sorl.thumbnail import ImageField


class Country(models.Model):
    """List of countries."""
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Timezone(models.Model):
    """List of timezones."""
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    """Fields common to tutors and students."""
    user = models.ForeignKey(User, unique=True)
    country = models.ForeignKey(Country, blank=True, null=True,
                                on_delete=models.PROTECT)
    state = models.CharField("State or Province", max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    bio = models.TextField("About", blank=True)
    picture = ImageField(upload_to='profile_pictures', blank=True, null=True)
    timezone = models.ForeignKey(Timezone, blank=True, null=True,
                                 on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        name = self.user.get_full_name()
        if name == '':
            name = self.user.username
        return name

    @models.permalink
    def get_absolute_url(self):
        return ('users_public_profile', (), {'pk': self.pk})

    def get_user_type(self):
        """Returns 'Tutor' or 'Student'."""
        if self.user.groups.filter(name='Students').exists():
            return 'Student'
        elif self.user.groups.filter(name='Tutors').exists():
            return 'Tutor'

    def get_location(self):
        """Returns 'city, state, country', or a subset if some are blank."""
        country = self.country.name if self.country else None
        return ', '.join([i for i in (self.city, self.state, country) if i])


class Student(UserProfile):
    """Extra profile fields and methods for students."""
    pass


class Tutor(UserProfile):
    """Extra profile fields and methods for tutors."""
    skills = models.TextField(blank=True)
    institution = models.CharField("Company/School/Institution", max_length=200,
                                  blank=True)
    other_qualifications = models.TextField(blank=True)
    #TODO: resume (from LinkedIn?)


@receiver(user_activated)
def create_blank_user_profile(sender, user, **kwargs):
    """Creates a blank user profile after an account is activated."""
    # Only run if user doesn't already have a profile
    try:
        user.get_profile()
    except ObjectDoesNotExist:
        if user.groups.filter(name='Students').exists():
            new_profile = Student(user=user)
            new_profile.save()
        elif user.groups.filter(name='Tutors').exists():
            new_profile = Tutor(user=user)
            new_profile.save()
