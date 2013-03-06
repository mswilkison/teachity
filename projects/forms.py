import re

from django import forms
from django.forms.models import inlineformset_factory

from .models import Bid
from .models import BidFile
from .models import Project
from .models import ProjectFile
from .models import RequiredSkill


class CleanedDecimalField(forms.DecimalField):
    """A DecimalField which strips leading non-numeric digits.

    If a user enters "USD$500.00" it will be saved as "500.00".
    """
    def to_python(self, value):
        value = re.sub(r'^[^\d.]+', '', value)
        return super(CleanedDecimalField, self).to_python(value)


class ProjectForm(forms.ModelForm):
    budget_type = forms.ChoiceField(widget=forms.RadioSelect(),
                                    initial='fixed',
                                    choices=(('fixed', 'Fixed'),
                                             ('hourly', 'Hourly')),
                                    label='Type of Budget')
    budget = CleanedDecimalField(max_digits=10,
                                 decimal_places=2,
                                 required=False)
    project_type = forms.ChoiceField(widget=forms.RadioSelect(),
                                  initial='one time',
                                  choices=(('one time', 'One Time'),
                                           ('recurring', 'Recurring')),
                                  label='Type of Project')

    class Meta:
        model = Project
        exclude = ('student', 'published', 'completed')


ProjectFileFormSet = inlineformset_factory(Project, ProjectFile, extra=1)
RequiredSkillFormSet = inlineformset_factory(Project, RequiredSkill, extra=1)


class BidForm(forms.ModelForm):
    budget = CleanedDecimalField(max_digits=10,
                                 decimal_places=2)

    class Meta:
        model = Bid
        exclude = ('project', 'tutor', 'budget_type', 'awarded', 'declined')


BidFileFormSet = inlineformset_factory(Bid, BidFile, extra=1)
