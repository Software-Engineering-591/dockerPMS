from backend.models import Driver
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

