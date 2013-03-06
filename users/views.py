from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import DetailView
from django.utils.decorators import method_decorator

from projects.views import ProjectListView

from .forms import UserForm
from .forms import UserProfileForm
from .forms import TutorProfileForm
from .models import UserProfile


class DashboardView(ProjectListView):
    """Displays the current user's dashboard.
    
    A student's dashboard shows all of the projects created by the student.
    A tutor's dashboard shows all projects the tutor has bid on.
    """
    def get_template_names(self):
        user = self.request.user
        if user.groups.filter(name='Students').exists():
            template = 'users/student-dashboard.html'
        elif user.groups.filter(name='Tutors').exists():
            template = 'users/tutor-dashboard.html'
        else:
            return HttpResponseRedirect('/')
        return template

    def get_queryset(self):
        queryset = super(DashboardView, self).get_queryset()
        user = self.request.user
        profile = user.get_profile()
        if user.groups.filter(name='Students').exists():
            queryset = queryset.filter(student=profile)
        elif user.groups.filter(name='Tutors').exists():
            queryset = queryset.filter(project_bids__tutor=profile).distinct()
        return queryset


class PublicProfileView(DetailView):
    """Public view of a user's profile."""
    context_object_name = 'userprofile'
    queryset = UserProfile.objects.filter(user__is_active=True)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PublicProfileView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        """Students and Tutors have different profile templates."""
        profile = self.get_object()
        if profile.get_user_type() == 'Student':
            return 'users/student_public_profile.html'
        elif profile.get_user_type() == 'Tutor':
            return 'users/tutor_public_profile.html'
        else:
            return 'users/base_public_profile'


def view_profile(request):
    """Currently redirects to profile edit page if not profile, else sends
        to public profile view."""
    user = request.user
    # Check for an existing profile
    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('users_edit_profile'))
    return HttpResponseRedirect(reverse('users_public_profile',
                                    kwargs={'pk': profile.id}))

@login_required
def edit_profile(request):
    """Allows a user to edit or create a profile.

    Presents different forms based on whether the user is a student or tutor.
    """
    user = request.user
    # Check for an existing profile
    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        profile = None

    # Fetch user type and appropriate form
    if user.groups.filter(name='Students').exists():
        user_type = 'student'
        extra_form = UserProfileForm
    elif user.groups.filter(name='Tutors').exists():
        user_type = 'tutor'
        if profile:
            profile = profile.tutor
        extra_form = TutorProfileForm

    # Populate forms from exisitng data and POST
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = extra_form(request.POST, request.FILES, instance=profile)
    else:
        user_form = UserForm(initial={'first_name': user.first_name,
                                      'last_name': user.last_name,
                                      'email': user.email})
        profile_form = extra_form(instance=profile)

    if user_form.is_valid() and profile_form.is_valid():
        user.first_name = user_form.cleaned_data['first_name']
        user.last_name = user_form.cleaned_data['last_name']
        user.email = user_form.cleaned_data['email']
        user.save()
        # Profile save process depends on whether we're creating it
        # or just editing.
        if profile:
            profile_form.save()
        else:
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
        # Redirect to public profile view
        return HttpResponseRedirect(reverse('users_public_profile',
                                            kwargs={'pk': profile.id}))

    return render_to_response('users/edit-profile.html',
                              {'user_form': user_form,
                               'profile_form': profile_form,
                               'user_type': user_type},
                              context_instance=RequestContext(request))
