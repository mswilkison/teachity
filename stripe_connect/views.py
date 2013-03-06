import requests
import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, QueryDict
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DetailView

from projects.models import Project

from .forms import StripeTransactionForm
from .models import StripeAccessKey
from .models import StripeTransaction


def check_user_for_stripe(user):
    """Takes a User instance and checks for an existing StripeAccessKey.
    
    Returns the key object if found, or False.
    """
    try:
        key = StripeAccessKey.objects.get(user=user)
        return key
    except StripeAccessKey.DoesNotExist:
        return False

# OAUTH FLOW
def oauth_start(request):
    """Redirects to Stripe to begin the account connection process.

    If the user already has a Stripe access key we don't attempt to get another
    key for them.
    """
    key = check_user_for_stripe(request.user)
    if key:
        return redirect('stripe_key_exists')

    qs = QueryDict('', mutable=True)
    qs.update({
        'response_type': 'code',
        'client_id': settings.STRIPE_CLIENT_ID,
        'scope': 'read_write'
    })
    return redirect('https://connect.stripe.com/oauth/authorize?' + qs.urlencode())

@login_required
def retrieve_token(request):
    """Retrieves an access token from Stripe's Connect API.

    If we already have an access token for this user we don't attempt to 
    fetch a new one.
    """
    user = request.user
    key = check_user_for_stripe(user)
    if key:
        return redirect('stripe_key_exists')

    code = request.GET.get('code')
    if not code:
        raise Http404

    r = requests.post(
        url='https://connect.stripe.com/oauth/token',
        headers={'Accept': 'application/json',
                 'Authorization': 'Bearer {0}'.format(settings.STRIPE_CLIENT_SECRET)},
                      data={'grant_type': 'authorization_code',
                      'client_id': settings.STRIPE_CLIENT_ID,
                      'scope': 'read_write',
                      'code': code})

    try:
        r.raise_for_status()
    except requests.HTTPError:
        return render_to_response('stripe_connect/oauth_failed.html',
                                  {},
                                  context_instance=RequestContext(request))

    token = r.json.get('access_token')
    access_key = StripeAccessKey(user=user, access_key=token)
    access_key.save()

    return render_to_response('stripe_connect/confirmation.html',
                              {},
                              context_instance=RequestContext(request))

@login_required
def key_exists(request):
    """Used to handle repeated attempts to connect a user's Stripe account."""
    return render_to_response('stripe_connect/key_exists.html',
                              {},
                              context_instance=RequestContext(request))


class TransactionCreateView(CreateView):
    """Handles the Stripe payment form."""
    model = StripeTransaction
    form_class = StripeTransactionForm

    def get_success_url(self):
        """The detailed view of our saved transaction."""
        return self.object.get_absolute_url()

    def form_valid(self, form):
        """Creates a Stripe charge and logs it.

        If Stripe returns errors we add them to the form's errors and display
        them to the user
        """
        project = self.get_context_data()['project']
        # Make sure user is allowed to make a payment
        user = self.request.user
        if user != project.student.user:
            raise PermissionDenied("You cannot add a payment for this project")

        payee = project.get_tutor().user
        stripe_token = self.request.POST.get('stripeToken', None)
        charge_description = 'Payment from %s to %s for project: %s' \
            % (user.get_full_name(), payee.get_full_name(), project)

        payment_amount = form.cleaned_data['amount']

        # Create Stripe charge
        try:
            charge = stripe.Charge.create(
                amount=payment_amount,
                currency=settings.STRIPE_CURRENCY,
                card=stripe_token,
                description=charge_description,
                application_fee=000, #Teachity charges the greater of $2 or 15% of total transaction amount
                api_key=check_user_for_stripe(payee),
            )
        except stripe.CardError, e:
            form.errors['__all__'] = e
            return self.form_invalid(form)

        # Fees for our transaction record
        charge_stripe_fee = 0
        charge_teachity_fee = 0
        for fee in charge.fee_details:
            if fee['type'] == 'stripe_fee':
                charge_stripe_fee = fee['amount']
            if fee['type'] == 'application_fee':
                charge_teachity_fee = fee['amount']

        # Save the transaction
        transaction = StripeTransaction(project=project,
                                        stripe_charge_id=charge.id,
                                        description=charge_description,
                                        currency=charge.currency,
                                        total_amount=charge.amount,
                                        stripe_fee=charge_stripe_fee,
                                        teachity_fee=charge_teachity_fee)
        transaction.save()
        self.object = transaction
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(TransactionCreateView, self).get_context_data(*args, **kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        context['project'] = project
        context['stripe_published_key'] = settings.STRIPE_PUBLISHABLE
        return context 

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TransactionCreateView, self).dispatch(*args, **kwargs)


class TransactionDetailView(DetailView):
    context_object_name = 'transaction'
    queryset = StripeTransaction.objects.all()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        dispatch = super(TransactionDetailView, self).dispatch(*args, **kwargs)
        project = self.get_object().project
        user = self.request.user
        if project.student.user == user or project.get_tutor().user == user:
            return dispatch
        raise PermissionDenied("You cannot view this transaction")
