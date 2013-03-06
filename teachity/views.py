from django.http import Http404
from django.template import TemplateDoesNotExist
from django.views.generic.simple import direct_to_template


def fetch_template(request, template_name):
    """Fetches a named template from the 'mockups' folder."""
    try:
        return direct_to_template(request, template='mockups/%s.html' % template_name)
    except TemplateDoesNotExist:
        raise Http404()
