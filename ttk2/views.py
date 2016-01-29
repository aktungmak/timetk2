from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from models import Netcode, User, Event
from forms import NewNetcodeForm

def activities(request):
    netcode_list = Netcode.objects.filter(enabled=True)
    ctx = {'netcode_list': netcode_list}
    return render(request, 'ttk2/activities.html', ctx)

def netcodes(request):
    # todo this should be current user
    u = User.objects.first()
    netcode_list = Netcode.objects.filter(user=u)
    ctx = {'netcode_list': netcode_list}
    if request.method == 'POST':
        form = NewNetcodeForm(request.POST)
        if form.is_valid():
            # process form.cleaned_data here
            n = u.netcode_set.create()
            n.network = request.POST['network']
            n.activity = request.POST['activity']
            n.name = request.POST['name']
            n.description = request.POST['description']
            n.save()
            return HttpResponseRedirect(reverse('netcodes'))
        else:
            ctx['error'] = unicode(form.errors)
            ctx['newnetcodeform'] = form
    else:
        ctx['newnetcodeform'] = NewNetcodeForm()

    return render(request, 'ttk2/netcodes.html', ctx)

def delnetcode(request, netcode_id):
    if request.method == 'POST':
        get_object_or_404(Netcode, pk=netcode_id).delete()
        return HttpResponseRedirect(reverse('netcodes'))
    else:
        return HttpResponseNotAllowed(['POST'])

def togglenetcode(request, netcode_id):
    if request.method == 'POST':
        n = get_object_or_404(Netcode, pk=netcode_id)
        n.enabled = not n.enabled
        n.save()
        return HttpResponseRedirect(reverse('netcodes'))
    else:
        return HttpResponseNotAllowed(['POST'])

def startstop(request, netcode_id):
    if request.method == 'POST':
        n = get_object_or_404(Netcode, pk=netcode_id)
        if n.curstart is None:
            # not running, lets start
            n.curstart = timezone.now()
        else:
            # running, stop and save
            e = n.event_set.create()
            e.start = n.curstart
            e.end = timezone.now()
            e.save()
            n.curstart = None
        n.save()
        return HttpResponseRedirect(reverse('activities'))
    else:
        return HttpResponseNotAllowed(['POST'])


def history(request, year, month, day):
    # todo this should be current user
    u = User.objects.first()
    event_list = Event.objects.filter(netcode__user=u, netcode__enabled=True)
    ctx = {'event_list': event_list}
    return render(request, 'ttk2/history.html', ctx)

def historynow(request):
    now = timezone.now()
    return HttpResponseRedirect(reverse('history', args=(now.year, now.month, now.day)))

def report(request, year, month, day):
    # todo this should be current user
    u = User.objects.first()
    event_list = Event.objects.filter(netcode__user=u, netcode__enabled=True)
    ctx = {'event_list': event_list}
    return render(request, 'ttk2/report.html', ctx)

def reportnow(request):
    now = timezone.now()
    return HttpResponseRedirect(reverse('report', args=(now.year, now.month, now.day)))

def editevent(request, event_id):
    return "hi"