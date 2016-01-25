from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import Netcode, User
from forms import NewNetcodeForm

def index(request):
    return HttpResponse('hej!')

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
            nn = u.netcode_set.create()
            nn.network = request.POST['network']
            nn.activity = request.POST['activity']
            nn.name = request.POST['name']
            nn.description = request.POST['description']
            nn.save()
            return HttpResponseRedirect(reverse('netcodes'))
        else:
            ctx['error'] = unicode(form.errors)
            ctx['newnetcodeform'] = form
    else:
        ctx['newnetcodeform'] = NewNetcodeForm()

    return render(request, 'ttk2/netcodes.html', ctx)

def delnetcode(request):
    HttpResponseRedirect(reverse('netcodes'))

def delnetcode(request, netcode_id):
    n = Netcode.get_object_or_404(pk=netcode_id).delete()
    return HttpResponseRedirect(reverse('activities'))

def history(request):
    return render(request, 'ttk2/history.html')

def report(request, start, end):
    return render(request, 'ttk2/reports.html')

def reportnow(request):
    return render(request, 'ttk2/reports.html')
