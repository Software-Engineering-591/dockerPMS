import dataclasses
import json
import math
from dataclasses import dataclass
from datetime import timedelta, datetime

from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
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
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from .forms import QuoteForm, MessageForm, TopUpForm, UserProfileForm, RegisterForm


# Create your views here.

# may be advisable to use hardcoded value 200 for total_space, unless 200 slots are going to be created
@require_GET
def home(request):
    total_space = get_total_space_total()
    reserved_space = get_reserved_space_total()
    if total_space > 0:
        available_space_percentage = (((total_space - reserved_space) / total_space) * 100)
        available_spaces = total_space - reserved_space
    else:
        available_space_percentage = 0
        available_spaces = 0
    return render(request, 'frontend/home.html', {'form': QuoteForm(), 'total_space': total_space,
                                                  'available_space_percentage': available_space_percentage,
                                                  'available_spaces': available_spaces})


@require_http_methods(['GET', 'POST'])
def signup(request):
    # POST
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            driver = Driver.objects.create(user=user)
            driver.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = RegisterForm()

    # GET
    context = {'form': form}
    return render(request, 'frontend/signup.html', context)


@require_http_methods(['GET', 'POST'])
def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        if user.is_superuser:
            return redirect('admin_dashboard')  # redirect to the admin dashboard if admin logged in
        else:
            return redirect('index')  # for the normal user (driver)return redirect('index')
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
    messages = admin.messages.filter(Q(sender=sender) | Q(sender=request.user))
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
        form = QuoteForm()

        lot_geodata = [
            LeafletLot(
                point=(lot.poly.centroid.y, lot.poly.centroid.x),
                poly=tuple(zip(lot.poly[0].y, lot.poly[0].x)),
                popup_html=render_to_string(
                    'frontend/reserve/popup.html', {'parkinglot': lot, 'form' : form}
                ),
            )
            for lot in ParkingLot.objects.all()
        ]
        return {
            'geo_data': json.dumps(lot_geodata, cls=EnhancedJSONEncoder), 'form' : form
        }

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

# class LotView(DetailView):
#     model = ParkingLot

def lot_view(request, pk):
    plot = get_object_or_404(ParkingLot, pk=pk)

    total = plot.get_total_space()
    available = plot.get_available_space()
    reserved = plot.get_reserved_space()
    slot = Slot.objects.filter(lot=plot, status=Slot.Status.AVAILABLE).first()
    driver = get_object_or_404(Driver, user=request.user.id)
    old_request = Request.objects.filter(driver_id=driver, status=Request.CurrentStatus.CREATED)
    if total > 0:
        available_progress = (((total - reserved) / total) * 100)
        reserved_progress = (((total - available) / total) * 100)
    else:
        available_progress = 0
        reserved_progress = 0
    if old_request is not None:
        old_request.delete()


    if request.method == 'POST':
        form = QuoteForm(request.POST)
        print(form)
        if form.is_valid():
            print("hello")
            request = Request.objects.create(
                driver_id=driver,
                slot=slot,
                arrival= datetime.combine(form.cleaned_data['date_from'], form.cleaned_data['time_from']),
                departure=datetime.combine(form.cleaned_data['date_to'], form.cleaned_data['time_to'])

            )
            request.save()
            return redirect('/quote/')
    else:
        form = QuoteForm()

        return render(request, 'frontend/lot.html', {'total': total, 'available': available,
                                                 'reserved': reserved, 'available_progress': available_progress,
                                                 'reserved_progress': reserved_progress, 'lot' : pk, 'form': form})


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
    return render(request, 'frontend/rp_history.html', {'request': requests, 'payments': payments})


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


    form = TopUpForm()
    user = get_object_or_404(User, username=request.user.username)
    driver = get_object_or_404(Driver, user=request.user.id)

    requested = Request.objects.all().filter(driver_id=driver, status=Request.CurrentStatus.CREATED).first()

    duration = requested.departure - requested.arrival

    parking_charge = calculate_parking_charge(duration)

    context = {
        'assigned_slot': requested.slot.lot.name,
        'user': user,
        'parking_charge': parking_charge,
        'current_credit': driver.credit,
        'form': form
    }
    if request.method == 'POST':

        form = TopUpForm(request.POST)
        driver = get_object_or_404(Driver, user=request.user.id)
        if form.is_valid():
            payment = Payment.objects.create(
                driver=driver,
                amount=form.cleaned_data['amount']
            )
            driver.credit += payment.amount
            driver.save()
            payment.save()
        return redirect('/quote')
    else:
        form = TopUpForm()
    return render(request, 'frontend/quote.html', context)
def calculate_parking_charge(duration):
    rate_per_hour = 100


    return rate_per_hour * math.ceil(duration.total_seconds() / 3600)

def make_quote(request):
    driver = get_object_or_404(Driver, user=request.user.id)
    requested = Request.objects.all().filter(driver_id=driver, status=Request.CurrentStatus.CREATED).first()
    requested.status = requested.CurrentStatus.PENDING

    duration = requested.departure - requested.arrival
    parking_charge = calculate_parking_charge(duration)
    driver.credit -= parking_charge
    driver.save()
    requested.save()
    return redirect('index')


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


@login_required()
def change_password(request: HttpRequest):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "frontend/profile/change_password.html", {
        'form': form
    })


@login_required()
def admin_dashboard(request):
    users = Driver.objects.all()
    parking_spaces = Slot.objects.all()
    occupied_space = get_reserved_space_total()
    available_space = get_available_space_total()
    total_space = get_total_space_total()
    unavailable_spaces = total_space - (occupied_space + available_space)
    if available_space > 0:
        available_space_percentage = (((total_space - available_space) / total_space) * 100)
    else:
        available_space_percentage = 0

    return render(request, "frontend/admin/admin_dashboard.html", {"Users": users, "total_space": total_space,
                                                                   "occupied_space": occupied_space, "available_space": available_space
                                                                   , "available_percentage" : available_space_percentage, "slots" : parking_spaces
                                                                   , "unavailable" : unavailable_spaces})


@login_required()
def admin_request(request):
    return render(request, "frontend/admin/admin_request.html")
