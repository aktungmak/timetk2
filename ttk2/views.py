import datetime

from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from models import Netcode, Event
from forms import NewNetcodeForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import authenticate, login
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'))
            login(request, user)
            return HttpResponseRedirect(reverse('activities'))
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def activities(request):
    netcode_list = Netcode.objects.filter(enabled=True, user=request.user)
    ctx = {'netcode_list': netcode_list}
    return render(request, 'ttk2/activities.html', ctx)

@login_required
def netcodes(request):
    netcode_list = Netcode.objects.filter(user=request.user)
    ctx = {'netcode_list': netcode_list}
    if request.method == 'POST':
        form = NewNetcodeForm(request.POST)
        if form.is_valid():
            # process form.cleaned_data here
            n = request.user.netcode_set.create()
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

@login_required
def delnetcode(request, netcode_id):
    if request.method == 'POST':
        get_object_or_404(Netcode, pk=netcode_id, user=request.user).delete()
        return HttpResponseRedirect(reverse('netcodes'))
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def togglenetcode(request, netcode_id):
    if request.method == 'POST':
        n = get_object_or_404(Netcode, pk=netcode_id, user=request.user)
        n.enabled = not n.enabled
        n.save()
        return HttpResponseRedirect(reverse('netcodes'))
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def startstop(request, netcode_id):
    if request.method == 'POST':
        n = get_object_or_404(Netcode, pk=netcode_id, user=request.user)
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

@login_required
def editstart(request, netcode_id):
    if request.method == 'POST':
        n = get_object_or_404(Netcode, pk=netcode_id, user=request.user)
        if not n.curstart is None and 'start' in request.POST:
            # only edit if running
            try:
                new = datetime.datetime.strptime(request.POST['start'], '%H:%M')
            except ValueError:
                pass
            else:
                print new
                n.curstart = n.curstart.replace(hour=new.hour, minute=new.minute)
                print n.curstart
                n.save()
        return HttpResponseRedirect(reverse('activities'))
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def history(request, year, month, day):
    try:
        now = timezone.datetime(*map(int, (year, month, day)))
    except ValueError:
        return HttpResponseNotFound("no such date!")


    # get all enabled events for this user, which either started or ended today
    event_list = Event.objects.filter(Q(netcode__user=request.user)
                                     &Q(netcode__enabled=True)
                                     &(Q(start__date=now)|Q(end__date=now)))

    ctx = {'event_list': event_list,
           'now': now.date(),
           'prev_day': now-timezone.timedelta(days=1),
           'next_day': now+timezone.timedelta(days=1),
    }
    return render(request, 'ttk2/history.html', ctx)

@login_required
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

@login_required
def report(request, year, month, day):
    event_list = Event.objects.filter(netcode__user=request.user, netcode__enabled=True)
    ctx = {'event_list': event_list}
    return render(request, 'ttk2/report.html', ctx)

def reportnow(request):
    now = timezone.now()
    return HttpResponseRedirect(reverse('report', args=(now.year, now.month, now.day)))

def editevent(request, event_id):
    if request.method == 'POST':
        e = get_object_or_404(Event, pk=event_id, netcode__user=request.user)

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
