from django.shortcuts import render_to_response
import django.contrib.auth as auth
from oj.volume.models import ProblemVolume
from oj.userprofile.views import  userpermitvolume
from django.template import RequestContext
from django.http import HttpResponseRedirect
from oj.judge.models import Judge

def volume_list(request):
    volume = ProblemVolume.objects.all()
    return render_to_response('volume/problemvolume_list.html', RequestContext(request, {'object_list':volume}) )

def volume_detail(request, object_id):
    volume = ProblemVolume.objects.get(id__exact = object_id)
    if userpermitvolume(request.user, volume):
        return render_to_response('volume/problemvolume_detail.html', RequestContext(request, {'object':volume}))
    else:
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html', RequestContext(request, {'errors':errors}))

def volume_regenerate(request, object_id):
    volume = ProblemVolume.objects.get(id__exact = object_id)
    for problem in volume.problem.all():
        problem.accept_counts = Judge.objects.filter(problem__exact = problem, result__exact = 'AC').count()
	problem.submit_counts = Judge.objects.filter(problem__exact = problem).count()
        problem.save()
    return HttpResponseRedirect('/oj/volume/%s/'%object_id)

