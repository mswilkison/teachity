from django import forms

from .models import Tutor
from .models import UserProfile


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=75, required=True)


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('user',)


class TutorProfileForm(UserProfileForm):

    class Meta(UserProfileForm.Meta):
        model = Tutor
