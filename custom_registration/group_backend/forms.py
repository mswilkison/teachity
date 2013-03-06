from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail


attrs_dict = {'class': 'required'}

class GroupSelectRegistrationForm(RegistrationFormUniqueEmail):
    user_group = forms.ChoiceField(widget=forms.RadioSelect(attrs=attrs_dict),
                                   choices=(('student', 'Student'),
                                            ('tutor', 'Tutor')),
                                   label=_("Type of user"))
