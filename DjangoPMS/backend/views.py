from django.contrib import auth
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Driver
# Create your views here.


@require_POST
def logout(request):
    auth.logout(request)
    return redirect('index')

@require_POST
def ban(request, pk):
    if hasattr(request.user, 'admin'):
        driver = get_object_or_404(Driver, pk=pk)
        driver.banned = True
        driver.save()
        return redirect("index")
    else:
        return HttpResponseForbidden(request, "You are not allowed")
@require_POST
@login_required
def unban(request, pk):
    if hasattr(request.user, 'admin'):
        driver = get_object_or_404(Driver, pk=pk)
        driver.banned = False
        driver.save()
        return redirect("index")
    return HttpResponseForbidden(request, "You are not allowed")