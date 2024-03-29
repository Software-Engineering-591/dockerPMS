from django.contrib import auth
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

# Create your views here.


@require_POST
def logout(request):
    auth.logout(request)
    return redirect('index')
