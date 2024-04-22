from backend.models import Driver
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from datetime import timedelta
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



@require_http_methods(["GET", "POST"])
def topup(request):
    if request.method == 'POST':
        form = TopUpForm(request.POST)
        if form.is_valid():
            # Here you would process the payment and top up the user's credit.
            # For now, let's assume the payment is successful and we redirect to a 'topup_success' page not sure if
            # we have a topup_success page in the design would be nice if we do or at least have some kind of indication that payment is succescfull
            return redirect('topup_success')
    else:
        form = TopUpForm()
        # Retrieve user's current credit and calculate the minimum required top-up if necessary.
        current_credit = request.user.profile.credit  # im not sure about the path
        total_charge = get_total_charge()  # I have not made a get total charge function
        min_topup = max(total_charge - current_credit, 0)  # Ensures a minimum top-up requirement.

        form.fields['amount'].initial = min_topup

    return render(request, "topup.html", {"form": form, "min_topup": min_topup})

#parking caculation
def calculate_parking(parked_time):


    # this is a code to calculate if the users can park for more than a day, im assuming they can't so i made another one where they cant
    #if parked_time >= timedelta(days=1):
       # days = parked_time.days
        # Calculate the charge for the full days
       # full_day_charge = days * daily_rate
        # Calculate the remainder hours charge
       # remainder_hours = total_hours - (days * 24)
      # remainder_charge = remainder_hours * hourly_rate
        # Total charge is full days plus remainder hours
       # total_charge = full_day_charge + remainder_charge
    #else:
        # For less than a day, calculate using the hourly rate
       # total_charge = total_hours * hourly_rate

    # Retrieve hourly rate from settings i dont know how to implement this in settings.py pls help
    hourly_rate = settings.PARKING_HOURLY_RATE

    # Calculate total hours parked
    total_hours = parked_time.total_seconds() / 3600  # convert seconds to hours

    # Calculate the charge using the hourly rate
    total_charge = total_hours * hourly_rate

    # If the parking duration doesn't round up to the next hour, and your policy is to charge for the full hour regardless,
    # you can use the math.ceil function to round up to the nearest whole number:
    # import math
    # total_charge = math.ceil(total_hours) * hourly_rate

    # Round the charge to 2 decimal places
    return round(total_charge, 2)


# In  settings.py file
settings.PARKING_HOURLY_RATE = 2.5



@login_required
@require_http_methods(["GET", "POST"])
def quote(request):
    # Use a form for GET and POST; for POST, the form will be filled with submitted data
    form = QuoteForm(request.POST or None)

    # mahie i dont know the variables for the assigned parking or their current credit please help ! :)
    assigned_slot = get_user_slot(request.user)
    current_credit = get_user_credit(request.user)

    if request.method == 'POST' and form.is_valid():


        # Redirect to confirmation_page i dont think we have do confirmation page do we ? but i do think it would be good to have one
        return redirect('confirmation_page')

    # Calculate the minimum top-up amount required if the parking_charge exceeds current_credit
    parking_charge = calculate_parking()  # Replace with your method to calculate charge
    min_topup = max(0, parking_charge - current_credit)

    # Add the minimum top-up to the form's context if necessary
    form.initial['min_topup'] = min_topup

    context = {
        'form': form,
        'assigned_slot': assigned_slot,
        'current_credit': current_credit,
        'min_topup': min_topup,
    }

    return render(request, "quote.html", context)