from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                      cd['subject'],
                      cd['message'],
                      cd.get('email', 'noreply@example.com'),
                      ['teachity@teachity.com'],
            )
            return HttpResponseRedirect('/contact/thanks/')
    else:
        form = ContactForm()
    return render_to_response('contact/contact_form.html', {'form': form},
                              context_instance=RequestContext(request))