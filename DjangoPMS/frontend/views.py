from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Create your views here.

def home(request):
    return render(request, 'frontend/home.html')




@require_http_methods(["GET", "POST"])
def login(request):
    pass
#     form = auth.forms.AuthenticationForm(request, data=request.POST)
#     if form.is_valid():
#         user = form.get_user()
#         auth.login(request, user)
#         return redirect('index')
#     return redirect('login')
