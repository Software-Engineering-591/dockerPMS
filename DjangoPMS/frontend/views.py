import dataclasses
import json
from dataclasses import dataclass
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from backend.models import Driver, Message, ParkingLot
from .forms import QuoteForm, MessageForm, UserProfileForm, RegisterForm


# Create your views here.


@require_GET
def home(request):
    return render(request, 'frontend/home.html', {'form': QuoteForm()})


@require_http_methods(['GET', 'POST'])
def signup(request:HttpRequest):
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
            return redirect('admin_dashboard') # redirect to the admin dashboard if admin logged in
        else:
            return redirect('index') # for the normal user (driver)

    return render(request, 'frontend/login.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def driver_messaging(request):
    messages = Message.objects.order_by('timestamp')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        admin = User.objects.get(is_superuser=True)
        if form.is_valid():
            message = form.save(commit=False)
            message.receiver = admin
            message.sender = request.user
            message.save()
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
    messages = Message.objects.order_by('timestamp')
    senders = Message.objects.order_by('sender').distinct('sender')
    return render(
        request,
        'frontend/message/admin.html',
        {'Messages': messages, 'Senders': senders},
    )


@require_http_methods(['GET', 'POST'])
def admin_message_ctx(request, sender):
    messages = Message.objects.filter(Q(sender=sender) | Q(receiver=sender))
    senders = Message.objects.order_by('sender').distinct('sender')
    driver = get_object_or_404(User, pk=sender)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.receiver = driver
            message.sender = request.user
            message.save()
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
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "frontend/profile/change_password.html", {
        'form': form
    })

@login_required()
def admin_dashboard(request):
    return render(request, "frontend/admin/admin_dashboard.html")


