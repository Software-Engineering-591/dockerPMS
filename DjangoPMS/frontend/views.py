from django.contrib.auth.models import User
from frontend.forms import messageForm
from dataclasses import dataclass
import json
import dataclasses

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from .forms import QuoteForm
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from backend.models import Driver, ParkingLot, Message

# Create your views here.


@require_GET
def home(request):
    return render(request, 'frontend/home.html', {'form': QuoteForm()})


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
def driverMessaging(request):
    messages = Message.objects.order_by('timestamp')
    if request.method == 'POST':
        form = messageForm(request.POST)
        admin = User.objects.get(is_superuser=True)
        if form.is_valid():
            message_temp = form.save(commit=False)
            message_temp.receiver = admin
            message_temp.sender = request.user
            message_temp.save()
            return redirect('/message/')
    else:
        form = messageForm()

    context = {'Messages': messages, 'form': form}

    return render(
        request,
        'frontend/driverMessage.html',
        {'form': form, 'Messages': messages},
    )


@require_http_methods(['GET', 'POST'])
def adminMessages(request):
    messages = Message.objects.order_by('timestamp')
    senders = Message.objects.order_by('sender').distinct('sender')
    return render(
        request,
        'frontend/adminMessage.html',
        {'Messages': messages, 'Senders': senders},
    )


@require_http_methods(['GET', 'POST'])
def adminMessageContext(request, sender):
    messages = Message.objects.filter(Q(sender=sender) | Q(receiver=sender))
    senders = Message.objects.order_by('sender').distinct('sender')
    driver = get_object_or_404(User, pk=sender)

    if request.method == 'POST':
        form = messageForm(request.POST)
        if form.is_valid():
            message_temp = form.save(commit=False)
            message_temp.receiver = driver
            message_temp.sender = request.user
            message_temp.save()
            return redirect(f'/adminMessage/{sender}/')
    else:
        form = messageForm()
    return render(
        request,
        'frontend/adminMessageContext.html',
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
    poly: list[latlng]
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
                popup_html=render_to_string('frontend/reserve/popup.html'),
            )
            for lot in ParkingLot.objects.all()
        ]
        return {
            'geo_data': json.dumps(lot_geodata, cls=EnhancedJSONEncoder),
        }
