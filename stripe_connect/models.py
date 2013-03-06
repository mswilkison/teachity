from django.contrib.auth.models import User
from django.db import models


from projects.models import Project

class StripeAccessKey(models.Model):
    """Stripe access keys for tutors"""
    user = models.ForeignKey(User, unique=True)
    access_key = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.access_key


class StripeTransaction(models.Model):
    """Record of payments made by students.
    
    Monetary amounts are stored in cents for easier compatibility with Stripe.
    """
    project = models.ForeignKey(Project, related_name='payments')
    stripe_charge_id = models.CharField(max_length=50)
    description = models.TextField()
    currency = models.CharField(max_length="10")
    total_amount = models.PositiveIntegerField()
    stripe_fee = models.PositiveIntegerField()
    teachity_fee = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('stripe_view_transaction', (), {'pk': self.pk})
