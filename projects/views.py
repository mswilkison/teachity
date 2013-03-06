from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.utils.decorators import method_decorator

from opentok import OpenTokSDK
from stripe_connect.forms import StripeTransactionForm

from .forms import BidForm
from .forms import BidFileFormSet
from .forms import ProjectForm
from .forms import ProjectFileFormSet
from .forms import RequiredSkillFormSet
from .models import Bid
from .models import Category
from .models import Classroom
from .models import Project


class ProjectMixin(object):
    """Contains common code for project creation and editing."""
    model = Project
    form_class = ProjectForm

    def get_context_data(self, **kwargs):
        """Views using this mixin must override this method or inherit from
        another class which implements get_context_data
        """
        context = super(ProjectMixin, self).get_context_data(**kwargs)
        if self.request.POST:
            context['requiredskill_formset'] = RequiredSkillFormSet(self.request.POST,
                                                                    instance=self.object)
            context['projectfile_formset'] = ProjectFileFormSet(self.request.POST,
                                                                self.request.FILES,
                                                                instance=self.object)
        else:
            context['requiredskill_formset'] = RequiredSkillFormSet(instance=self.object)
            context['projectfile_formset'] = ProjectFileFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        """Views using this mixin must override this method or call it after
        setting self.object
        """
        context = self.get_context_data()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        requiredskill_formset = context['requiredskill_formset']
        projectfile_formset = context['projectfile_formset']
        if form.is_valid() and requiredskill_formset.is_valid() and projectfile_formset.is_valid:
            return self.form_valid(form,
                                   requiredskill_formset,
                                   projectfile_formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, requiredskill_formset, projectfile_formset):
        if 'project_post' in self.request.POST:
            self.object.published = True
        self.object.save()
        # Handle required skills
        requiredskill_formset.instance = self.object
        requiredskill_formset.save()
        # Handle project files
        projectfile_formset.instance = self.object
        projectfile_formset.save()
        return super(ProjectMixin, self).form_valid(form)


class ProjectCreateView(ProjectMixin, CreateView):
    """Handles project creation.

    This includes required skills and project files as inline formsets.
    """

    def form_valid(self, form, requiredskill_formset, projectfile_formset):
        self.object = form.save(commit=False)
        self.object.student = self.request.user.get_profile().student
        return super(ProjectCreateView, self).form_valid(form,
                                                         requiredskill_formset,
                                                         projectfile_formset)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        dispatch = super(ProjectCreateView, self).dispatch(*args, **kwargs)
        # Make sure we're dealing with a student
        # TODO: Create and use permissions for this instead
        if self.request.user.groups.filter(name='Students').exists():
            return dispatch
        raise PermissionDenied("Only students can create projects")

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(ProjectCreateView, self).post(request, *args, **kwargs)


class ProjectUpdateView(ProjectMixin, UpdateView):
    """Handles project editing.

    This includes required skills and project files as inline formsets.
    """

    def form_valid(self, form, requiredskill_formset, projectfile_formset):
        self.object = form.save()
        return super(ProjectUpdateView, self).form_valid(form,
                                                         requiredskill_formset,
                                                         projectfile_formset)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        dispatch = super(ProjectUpdateView, self).dispatch(*args, **kwargs)
        # Projects can only be edited by the student who created them
        student = self.get_object().student
        if self.request.user == student.user:
            return dispatch
        raise PermissionDenied("You don't have permission to edit this project")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ProjectUpdateView, self).post(request, *args, **kwargs)


class ProjectListView(ListView):
    """A paginated list of projects.

    Includes filtering based on request querystring.
    """
    context_object_name = 'project_list'
    paginate_by = 6

    def get_filtered_category(self):
        """
        Reurns a category based on the querystring or None if nothing is found.
        """
        category_id = self.request.GET.get('c', None)
        if category_id:
            try:
                return Category.objects.get(pk=category_id)
            except (ValueError, Category.DoesNotExist):
                pass
        return None

    def get_filtered_status(self):
        """The status requested in the querystring (if any)."""
        status = self.request.GET.get('s', None)
        if status:
            return status.title()
        return None

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectListView, self).get_context_data(*args, **kwargs)
        # Categories for filter list
        context['categories'] = Category.objects.all()
        # Search criteria
        search_category = self.get_filtered_category()
        if search_category:
            context['search_category'] = search_category
        search_status = self.get_filtered_status()
        if search_status:
            context['search_status'] = search_status
        return context

    def get_queryset(self):
        """Handles extra filtering based on querystring."""
        queryset = Project.objects.filter(published=True)
        category = self.get_filtered_category()
        if category is not None:
            queryset = queryset.filter(category=category)
        status = self.get_filtered_status()
        if status:
            if status == 'Closed':
                queryset = queryset.filter(completed=True)
            elif status == 'Awarded':
                queryset = queryset.filter(is_awarded=True)
            elif status == 'Open':
                queryset = queryset.filter(completed=False, is_awarded=False)

        queryset = queryset.order_by('-created')
        return queryset
        
    def dispatch(self, *args, **kwargs):
        return super(ProjectListView, self).dispatch(*args, **kwargs)


class ProjectDetailView(DetailView):
    """Detailed view of a project.

    Allows logged-in users to view published projects. Also shows draft
    projects to their creators.

    The creator of a project sees all bids submitted to the project, while
    tutors only see their own bids.
    """
    context_object_name = 'project'
    queryset = Project.objects.all()

    def get_object(self, queryset=None):
        project = super(ProjectDetailView, self).get_object(queryset)
        # If project isn't published, only the student who created it
        # can view it.
        if not project.published:
            if project.student.user != self.request.user:
                raise Http404()
        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        project = self.object
        user = self.request.user
        if project.student.user == user:
            context['bid_list'] = project.project_bids.all().order_by('-created')
            context['stripe_payment_form'] = StripeTransactionForm()
            context['stripe_published_key'] = settings.STRIPE_PUBLISHABLE
        else:
            context['bid_list'] = project.project_bids.filter(tutor__user=user).order_by('-created')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDetailView, self).dispatch(*args, **kwargs)


class BidSavedView(ProjectDetailView):
    """Detailed view of a project after submitting a bid."""

    def get_context_data(self, **kwargs):
        context = super(BidSavedView, self).get_context_data(**kwargs)
        context['bid_saved'] = True
        return context


class BidUpdateView(UpdateView):
    """Handles bid editing with bid files as an inline."""
    model = Bid
    form_class = BidForm
    template_name_suffix = '_edit_form'

    def get_success_url(self):
        url = self.object.project.get_absolute_url()
        return url

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        dispatch = super(BidUpdateView, self).dispatch(*args, **kwargs)
        tutor = self.get_object().tutor
        if self.request.user == tutor.user:
            return dispatch
        raise PermissionDenied("You don't have permission to edit this bid")

    def get_context_data(self, **kwargs):
        context = super(BidUpdateView, self).get_context_data(**kwargs)
        context['project'] = self.object.project
        if self.request.POST:
            context['bidfile_formset'] = BidFileFormSet(self.request.POST,
                                                        self.request.FILES,
                                                        instance=self.object)
        else:
            context['bidfile_formset'] = BidFileFormSet(instance=self.object)
        return context

    def get_object(self, *args, **kwargs):
        obj = super(BidUpdateView, self).get_object(*args, **kwargs)
        if obj.budget_type != obj.project.budget_type:
            obj.budget = None
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        bidfile_formset = context['bidfile_formset']
        if form.is_valid() and bidfile_formset.is_valid():
            return self.form_valid(form, bidfile_formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, bidfile_formset):
        self.object = form.save()
        self.object.save(update_budget_type=True)
        # Handle bid files
        bidfile_formset.instance = self.object
        bidfile_formset.save()
        return super(BidUpdateView, self).form_valid(form)
        

@login_required
def create_bid(request, project_id):
    """Handles bid submissions from the bid form on the project detail page.

    GET requests to this view are redirected to the detail view for the
    appropriate project.
    """
    user = request.user
    # Make sure we're dealing with a tutor
    # TODO: Create and use permissions for this instead
    if user.groups.filter(name='Tutors').exists():
        tutor = user.get_profile().tutor
    else:
        raise PermissionDenied("Only tutors can submit bids.")
    # Make sure this project is eligible to receive bids
    project = get_object_or_404(Project, pk=project_id)
    if project.get_status() != 'Open':
        raise PermissionDenied("This project is not open to bids.")

    if request.method == 'POST':
        bid_form = BidForm(request.POST)
        bidfile_formset = BidFileFormSet(request.POST, request.FILES)
        if bid_form.is_valid() and bidfile_formset.is_valid():
            bid = bid_form.save(commit=False)
            bid.project = project
            bid.tutor = tutor
            bid.save()
            ctx_dict = {'site': 'Teachity', 'title': project.title, 'project_id': project_id}
            subject = render_to_string('projects/bid_email_subject.txt', ctx_dict)
            message = render_to_string('projects/bid_email.txt', ctx_dict)
            project.student.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
            bidfile_formset.instance = bid
            bidfile_formset.save()
            return HttpResponseRedirect(reverse('projects_bid_saved',
                                                kwargs={'pk': project_id}))

        return render_to_response('projects/project_detail.html',
                                  {'bid_form': bid_form,
                                   'bidfile_formset': bidfile_formset,
                                   'project': project},
                                  context_instance=RequestContext(request))

    else:
        return HttpResponseRedirect(reverse('projects_view_detail',
                                            kwargs={'pk': project_id}))


@login_required
def classroom(request, project_id):
    """Displays the chatroom for a project.
    
    Only the project's student and tutor are allowed to join.
    """
    project = get_object_or_404(Project, pk=project_id)
    if not project.is_awarded:
        raise PermissionDenied("Only awarded projects have classrooms.")
    user = request.user
    project_student = project.student
    project_tutor = project.get_tutor()
    if project_student.user != user and project_tutor.user != user:
        raise PermissionDenied("Only the project's student or tutor can join"
                               " this room.")

    # Get or create the classroom for this project
    try:
        classroom = Classroom.objects.get(project=project)
    except Classroom.DoesNotExist:
        classroom = Classroom.create(project=project)

    # Get any archived chat messages
    chatlog = classroom.chat_entries.order_by('created')

    # Create a TokBox auth token for this user
    api_key = settings.TOKBOX_API_KEY
    api_secret = settings.TOKBOX_API_SECRET
    opentok_sdk = OpenTokSDK.OpenTokSDK(api_key, api_secret)
    token = opentok_sdk.generate_token(classroom.session_id)

    return render_to_response('projects/classroom.html',
                              {'tokbox_session_id': classroom.session_id,
                               'tokbox_api_key': api_key,
                               'tokbox_token': token,
                               'classroom': classroom,
                               'project': project,
                               'chatlog': chatlog,
                               'stripe_payment_form': StripeTransactionForm(),
                               'stripe_published_key': settings.STRIPE_PUBLISHABLE,
                              },
                              context_instance=RequestContext(request))
