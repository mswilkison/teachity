from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.html import escape

from dajaxice.decorators import dajaxice_register

from .forms import BidForm
from .forms import BidFileFormSet
from .models import Bid
from .models import Classroom
from .models import Project


@login_required
@dajaxice_register(method='GET')
def get_bid_form(request, project_id):
    """Loads the bid form into the project detail page."""
    project = get_object_or_404(Project, pk=project_id)
    if project.get_status() != 'Open':
        raise PermissionDenied("This project is not open to bids.")
    bid_form = BidForm()
    bidfile_formset = BidFileFormSet()
    return render_to_response('projects/bid_form.html',
                              {'bid_form': bid_form,
                               'bidfile_formset': bidfile_formset,
                               'project': project},
                              context_instance=RequestContext(request))

@dajaxice_register
@login_required
def decline_bid(request, project_id, bid_id):
    """Declines the selected bid."""
    project = get_object_or_404(Project, pk=project_id)
    bid = get_object_or_404(Bid, pk=bid_id)
    if bid.project != project:
        raise PermissionDenied("Bid is not associated with project.")
    if bid.project.student != project.student:
        raise PermissionDenied("You do not have permission to alter bids on this project.")
    bid.awarded = False
    bid.declined = True
    bid.save()
    return simplejson.dumps({'message': 'Bid declined',
                             'bid_id': bid.id})

@dajaxice_register
@login_required
def award_project(request, project_id, bid_id):
    """Awards the project to the selected bid."""
    project = get_object_or_404(Project, pk=project_id)
    bid = get_object_or_404(Bid, pk=bid_id)
    if bid.project != project:
        raise PermissionDenied("Bid is not associated with project.")
    if bid.project.student != project.student:
        raise PermissionDenied("You do not have permission to alter bids on this project.")
    if bid.project.get_status() != "Open":
        raise PermissionDenied("Only open projects can be awarded.")
    bid.declined = False
    bid.awarded = True
    bid.save()
    return simplejson.dumps({'message': 'Bid awarded',
                             'bid_id': bid.id})

@dajaxice_register
@login_required
def chat_message(request, classroom_id, message):
    """
    Saves classroom chat messages to the DB and returns them in TokBox-ready format.
    """
    user = request.user
    classroom = get_object_or_404(Classroom, pk=classroom_id)
    project = classroom.project
    project_student = project.student
    project_tutor = project.get_tutor()
    if project_student.user != user and project_tutor.user != user:
        raise PermissionDenied("Only the project's student or tutor can add"
                               " messages to this room.")
    message = classroom.chat_entries.create(user=user, message=message)
    # TokBox's StateManager eats single backslashes.
    safe_message = escape(message.message).replace('\\', '\\\\')
    safe_username = escape(message.user.get_full_name()).replace('\\', '\\\\')
    if safe_username == '':
        safe_username = message.user.username
    # Generating HTML here rather than in the template because TokBox's
    # StateManager can only set a single string at a time.
    message_html = '<div class="chat-message" data-message_id="%s"><p>%s: %s</p></div>' % (message.id, safe_username, safe_message)
    return simplejson.dumps({'message_html': message_html})
