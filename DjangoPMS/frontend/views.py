import dataclasses
import json
from dataclasses import dataclass

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from backend.models import Driver, Message, ParkingLot, Slot, Payment
from django.shortcuts import render, redirect
from backend.models import Driver, Message, ParkingLot, Request, Slot, Payment, Admin


from .forms import QuoteForm, MessageForm, TopUpForm, UserProfileForm, RegisterForm

# Create your views here.

# may be advisable to use hardcoded value 200 for total_space, unless 200 slots are going to be created
@require_GET
def home(request):
    total_space = get_total_space_total()
    reserved_space = get_reserved_space_total()
    if total_space > 0:
        available_space_percentage = (((total_space - reserved_space) / total_space)*100)
        available_spaces = total_space - reserved_space
    else:
        available_space_percentage = 0
        available_spaces = 0
    return render(request, 'frontend/home.html', {'form': QuoteForm(), 'total_space': total_space,
                                                  'available_space_percentage' : available_space_percentage,
                                                  'available_spaces':available_spaces})


@require_http_methods(['GET', 'POST'])
def signup(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        driver = Driver.objects.create(user=user)
        driver.save()
        auth.login(request, user)
        return redirect('index')
    return render(request, 'frontend/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        return redirect('index')
    return render(request, 'frontend/login.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def driver_messaging(request):
    driver = Driver.objects.get(user=request.user)
    messages = driver.messages
    if request.method == 'POST':
        form = MessageForm(request.POST)
        admin = User.objects.get(is_superuser=True)
        if form.is_valid():
            message = form.save(commit=False)
            message.receiver = admin
            driver.send_message(message)
            return redirect('/message/')
    else:
        form = MessageForm()

    context = {'Messages': messages, 'form': form}

    return render(
        request,
        'frontend/message/driver.html',
        {'form': form, 'Messages': messages},
    )


@require_http_methods(['GET', 'POST'])
def admin_messages(request):
    senders = Message.objects.order_by('sender').distinct('sender')
    return render(
        request,
        'frontend/message/admin.html',
        {'Senders': senders},
    )


@require_http_methods(['GET', 'POST'])
def admin_message_ctx(request, sender):
    admin = Admin.objects.get(user=request.user)
    messages = admin.messages
    senders = Message.objects.order_by('sender').distinct('sender')
    driver = get_object_or_404(User, pk=sender)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.receiver = driver
            message.sender = request.user
            admin.send_message(message)
            return redirect('msg_ctx', sender)
    else:
        form = MessageForm()
    return render(
        request,
        'frontend/message/admin_ctx.html',
        {
            'Messages': messages,
            'Senders': senders,
            'form': form,
            'Sender': driver,
        },
    )


@require_GET
def contact(request):
    return render(request, 'frontend/contact.html')


latlng = tuple[float, float]


@dataclass(slots=True, frozen=True)
class LeafletLot:
    point: latlng
    poly: tuple[latlng]
    popup_html: str


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class ReserveView(TemplateView):
    template_name = 'frontend/reserve/init.html'

    def get_context_data(self, **kwargs):
        lot_geodata = [
            LeafletLot(
                point=(lot.poly.centroid.y, lot.poly.centroid.x),
                poly=tuple(zip(lot.poly[0].y, lot.poly[0].x)),
                popup_html=render_to_string(
                    'frontend/reserve/popup.html', {'parkinglot': lot}
                ),
            )
            for lot in ParkingLot.objects.all()
        ]
        return {
            'geo_data': json.dumps(lot_geodata, cls=EnhancedJSONEncoder),
            'form': QuoteForm(self.request.POST),
        }

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


# class LotView(DetailView):
#     model = ParkingLot

def lot_view(request, pk):
    lot = ParkingLot.objects.get(pk=pk)
    total = lot.get_total_space()
    available = lot.get_available_space()
    reserved = lot.get_reserved_space()
    if total > 0:
        available_progress = (((total - reserved) / total)*100)
        reserved_progress = (((total - available) / total) * 100)
    else:
        available_progress = 0
        reserved_progress = 0
    return render(request,'frontend/lot.html', {'total': total, 'available': available,
                                                'reserved': reserved, 'available_progress' : available_progress, 'reserved_progress' : reserved_progress})

@login_required()
def messaging(request, sender=None):
    if (request.user.is_staff or request.user.is_superuser):
        return (
            admin_message_ctx(request, sender)
            if sender
            else admin_messages(request)
        )

    else:
        return driver_messaging(request)

@login_required
def request_and_payment(request):
    driver = Driver.objects.get(user=request.user)
    requests = Request.objects.all().filter(driver_id=driver.id).order_by('-timestamp')
    payments = Payment.objects.all().filter(driver=driver.id).order_by('-timestamp')
    return render(request, 'frontend/rp_history.html', {'request' : requests, 'payments' : payments})



def get_total_space_total():
    return Slot.objects.count()
def get_reserved_space_total():
    return Slot.objects.filter(status='R').count()

def get_available_space_total():
    return Slot.objects.filter(status='A').count()

class AdminView(TemplateView):
    template_name = 'frontend/admin.html'




@login_required
def quote(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            # Extract validated data
            date_from = form.cleaned_data['date_from']
            time_from = form.cleaned_data['time_from']
            date_to = form.cleaned_data['date_to']
            time_to = form.cleaned_data['time_to']

            # Combine dates and times into datetime objects
            datetime_from = datetime.datetime.combine(date_from, time_from)
            datetime_to = datetime.datetime.combine(date_to, time_to)

            # Calculate total duration in hours
            duration = (datetime_to - datetime_from).total_seconds() / 3600

            # Fetch an available parking slot
            available_slot = Slot.objects.filter(status=Slot.Status.AVAILABLE).first()

            if available_slot:
                # Assuming a cost calculation based on duration and a rate
                parking_charge = calculate_parking_charge(duration)

                # Prepare the context with all needed information
                context = {
                    'assigned_slot': available_slot.number,
                    'user': request.user,
                    'duration': duration,
                    'parking_charge': parking_charge,
                    'current_credit': request.user.driver.credit,
                    'form': form
                }
                return render(request, 'quote.html', context)
            else:
                form.add_error(None, 'No available parking slots.')
        else:
            # Form is not valid, re-render the page with existing form data
            return render(request, 'frontend/quote.html', {'form': form})
    else:
        form = QuoteForm()  # An unbound form for GET request

    return render(request, 'frontend/quote.html', {'form': form})

def calculate_parking_charge(duration):
    rate_per_hour = 250  # Set the rate per hour as needed
    return rate_per_hour * duration

def topup(request):
    if request.method == 'POST':
        form = TopUpForm(request.POST)
        if form.is_valid():
            # Process the payment here (integrate with your payment gateway)
            # For now, we'll assume the payment is processed successfully
            return redirect('success_url')  # Redirect to a success page
        else:
            # Form is not valid, return to the top-up page with errors
            return render(request, 'frontend/topup.html', {'form': form})
    else:
        form = TopUpForm()  # An unbound form for GET request
        return render(request, 'frontend/topup.html', {'form': form})

@require_http_methods(["GET", "POST"])
@login_required()
def profile(request: HttpRequest):
    user = request.user

    # POST
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("profile"))
    else:
        form = UserProfileForm()

    # GET
    form = UserProfileForm(instance=user)
    context = {
        "form": form,
    }
    return render(request, "frontend/profile/profile.html", context)