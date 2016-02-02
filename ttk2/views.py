import datetime

from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.exceptions import ValidationError

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
    try:
        now = timezone.datetime(*map(int, (year, month, day)))
    except ValueError:
        return HttpResponseNotFound("no such date!")

    # todo this should be current user
    u = User.objects.first()

    # get all enabled events for this user, which either started or ended today
    event_list = Event.objects.filter(Q(netcode__user=u)
                                     &Q(netcode__enabled=True)
                                     &(Q(start__date=now)|Q(end__date=now)))

    ctx = {'event_list': event_list,
           'now': now.date(),
           'prev_day': now-timezone.timedelta(days=1),
           'next_day': now+timezone.timedelta(days=1),
    }
    return render(request, 'ttk2/history.html', ctx)

def historynow(request):
    now = timezone.now()
    if request.method == 'POST':
        datestr = request.POST['date']
        datestr.replace('/', '-')
        try:
            date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        except ValueError:
            return HttpResponseRedirect(reverse('history', args=(now.year, now.month, now.day)))
        else:
            return HttpResponseRedirect(reverse('history', args=(date.year, date.month, date.day)))
    else:
        return history(request, now.year, now.month, now.day)

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
    if request.method == 'POST':
        e = get_object_or_404(Event, pk=event_id)

        if 'start' in request.POST:
            olddate = e.start
            try:
                nd = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
            else:
                e.start = timezone.make_aware(nd)
        elif 'end' in request.POST:
            olddate = e.end
            try:
                nd = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
            else:
                e.end = timezone.make_aware(nd)
        else:
            return HttpResponseBadRequest()

        try:
            e.full_clean()
        except ValidationError as e:
            pass
        else:
            # only save if validation is successful
            e.save()
        # use the old date to redirect to
        return HttpResponseRedirect(reverse('history', args=(olddate.year, olddate.month, olddate.day)))
    else:
        return HttpResponseNotAllowed(['POST'])
