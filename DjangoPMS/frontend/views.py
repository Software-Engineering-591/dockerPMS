from backend.models import Driver, Message
from django.contrib.auth.models import User
from frontend.forms import MessageForm
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET

# Create your views here.


@require_GET
def home(request):
    return render(request, "frontend/home.html")

@require_http_methods(["GET", "POST"])
def signup(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        driver = Driver.objects.create(user=user)
        driver.save()
        auth.login(request, user)
        return redirect("index")
    return render(request, "frontend/signup.html", {"form": form})

@require_http_methods(["GET", "POST"])
def login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        return redirect('index')
    return render(request, "frontend/login.html", {"form": form})

@require_http_methods(["GET", "POST"])
def DriverMessaging(request):
    Messages = Message.objects.order_by("timestamp")
    if request.method == "POST":
        form = MessageForm(request.POST)
        admin = User.objects.get(username="admin")
        if form.is_valid():
            Message_temp = form.save(commit=False)
            Message_temp.receiver = admin
            Message_temp.sender = request.user
            Message_temp.save()
            return redirect('/Message/')
    else:
        form = MessageForm()

    context = {
        "Messages" : Messages,
        "form" : form
    }

    return render(request, "frontend/DriverMessage.html", {"form": form, "Messages" : Messages})

# @require_http_methods(["GET", "POST"])
# def AdminMessages(request):
#     Messages = Message.objects.order_by("timestamp")
#     senders = Message.objects.order_by('sender').distinct('sender')
#     return render(request, "frontend/adminMessage.html", {"Messages" : Messages, "Senders" : senders})