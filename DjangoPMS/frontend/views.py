import dataclasses
import json
from dataclasses import dataclass

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from backend.models import Driver, Message, ParkingLot, Slot, BaseUser, Admin, Request, Payment

from .forms import QuoteForm, MessageForm

# Create your views here.


@require_GET
def home(request):
    available_space = get_available_space_api
    return render(request, 'frontend/home.html', {'form': QuoteForm(), 'available_space': available_space})


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


class LotView(DetailView):
    model = ParkingLot
    template_name = 'frontend/lot.html'


@login_required()
def messaging(request, sender=None):
    if hasattr(request.user, 'admin'):
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
    requests = Request.objects.all().filter(driver_id=driver.id)
    payments = Payment.objects.all().filter(driver=driver.id).order_by('timestamp')
    return render(request, 'frontend/requestPaymentHistory.html', {'request' : requests, 'payments' : payments})
def get_total_space_api():
    return ParkingLot.get_total_space
@require_GET
def get_reserved_space_api():
    return ParkingLot.get_reserved_space
def get_available_space_api():
    return ParkingLot.get_available_space()