
from django.contrib import auth
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Driver, Slot, Request


# Create your views here.


@require_POST
def logout(request):
    messages.success(request, 'You have been logged out!')
    auth.logout(request)
    return redirect('index')


@require_POST
def ban(request, pk):
    if hasattr(request.user, 'admin'):
        driver = get_object_or_404(Driver, pk=pk)
        driver.banned = True
        driver.save()
        return redirect('index')
    else:
        return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def unban(request, pk):
    if hasattr(request.user, 'admin'):
        driver = get_object_or_404(Driver, pk=pk)
        driver.banned = False
        driver.save()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def remove(request, slot_pk):
    if hasattr(request.user, 'admin'):
        slot = get_object_or_404(Slot, pk=slot_pk)
        slot.delete()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def block(request, slot_pk):
    if hasattr(request.user, 'admin'):
        slot = get_object_or_404(Slot, pk=slot_pk)
        slot.status = slot.Status.DISABLED
        slot.driver = None
        slot.save()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def free(request, slot_pk):
    if hasattr(request.user, 'admin'):
        slot = get_object_or_404(Slot, pk=slot_pk)
        slot.status = slot.Status.AVAILABLE
        slot.driver = None
        slot.save()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def accept(request, request_pk):
    if hasattr(request.user, 'admin'):
        requested = get_object_or_404(Request, pk=request_pk)
        requested.status = Request.CurrentStatus.APPROVED
        slot = requested.slot
        slot.driver = requested.driver_id
        slot.status = Slot.Status.RESERVED
        slot.save()
        requested.save()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')


@require_POST
@login_required
def reject(request, request_pk):
    if hasattr(request.user, 'admin'):
        requested = get_object_or_404(Request, pk=request_pk)
        requested.status = Request.CurrentStatus.REJECTED
        requested.save()
        return redirect('index')
    return HttpResponseForbidden(request, 'You are not allowed')
