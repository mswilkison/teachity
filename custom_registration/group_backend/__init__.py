from django.contrib.auth.models import Group

from registration.backends.default import DefaultBackend

from .forms import GroupSelectRegistrationForm


class GroupBackend(DefaultBackend):
    """
    A django-registration backend which extends the behaviour of the built-in
    DefaultBackend in one way: registering users are asked to select whether
    they are a tutor or student and their new account is assigned to the
    appropriate group.

    """
    def register(self, request, **kwargs):
        """
        Calls DefaultBackend.register and assigns the new user to a group.

        """
        user_group = kwargs['user_group']
        new_user = super(GroupBackend, self).register(request, **kwargs)
        if user_group == 'student':
            group, created = Group.objects.get_or_create(name='Students')
        elif user_group == 'tutor':
            group, created = Group.objects.get_or_create(name='Tutors')
        else:
            group = None
        if group:
            new_user.groups.add(group)
        return new_user

    def get_form_class(self, request):
        """
        Return our custom form class used for user registration.
        
        """
        return GroupSelectRegistrationForm
