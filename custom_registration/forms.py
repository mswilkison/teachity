from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import UNUSABLE_PASSWORD


class UsernamePasswordResetForm(PasswordResetForm):
    """Extends the built-in password reset form to include a username field.

    Both fields are optional (but at least one must be filled in).
    We attempt to find a user matching username, falling back to email address
    if necessary.
    """
    error_messages = {
        'unknown': _("We can't find a user account using this "
                     "information. Are you sure you've registered?"),
        'unusable': _("This user account cannot reset the password."),
    }
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(),
                                label=_("Username"),
                                required=False,
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("E-mail"), required=False, max_length=75)

    def clean(self):
        """Finds a user or users based on username and email."""
        try:
            email = self.cleaned_data["email"]
        except KeyError:
            email = ''
        try:
            username = self.cleaned_data["username"]
        except KeyError:
            username = ''
        if not username and not email:
            raise forms.ValidationError(_("Please provide a username or email address."))
        self.users_cache = ()
        # Try to find an exact username match
        if username:
            self.users_cache = User.objects.filter(username__iexact=username,
                                                   is_active=True)
        # No users found, fall back to email
        if not len(self.users_cache) and email:
            self.users_cache = User.objects.filter(email__iexact=email,
                                                   is_active=True)
        # Still no users, raise an error
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD) for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return self.cleaned_data

    def clean_email(self):
        return self.cleaned_data["email"]
