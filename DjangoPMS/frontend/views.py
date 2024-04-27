from backend.models import Driver
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.contrib import messages
from django.conf import settings

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


def topup(request):
    min_topup = 10.00  # Example minimum top-up amount

    if request.method == 'POST':
        top_up_amount = request.POST.get('amount', 0)
        if float(top_up_amount) >= min_topup:
            messages.success(request, 'Your account has been successfully topped up by £{}.'.format(top_up_amount))
        else:
            messages.error(request, 'The top-up amount must be at least £{}.'.format(min_topup))

    return render(request, 'frontend/topup.html', {'min_topup': min_topup})

#parking caculation
def calculate_parking(parked_time):

    # Retrieve hourly rate from settings i dont know how to implement this in settings.py pls help
    hourly_rate = settings.PARKING_HOURLY_RATE

    # Calculate total hours parked
    total_hours = parked_time.total_seconds() / 3600  # convert seconds to hours

    # Calculate the charge using the hourly rate
    total_charge = total_hours * hourly_rate


    # Round the charge to 2 decimal places
    return round(total_charge, 2)


# In  settings.py file
settings.PARKING_HOURLY_RATE = 250




@require_http_methods(["GET", "POST"])
def quote(request):
    # Assume these values are fetched or calculated appropriately
    assigned_slot = 'A110'
    current_credit = 100.00  # Example user credit
    parking_charge = 280  # Example parking charge

    context = {
        'assigned_slot': assigned_slot,
        'current_credit': current_credit,
        'parking_charge': parking_charge,
    }

    return render(request, 'frontend/quote.html', context)