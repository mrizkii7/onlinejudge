from django.conf.urls.defaults import *
from django.conf import settings
from oj.problem.models import Problem
from oj.judge.models import Judge
from oj.volume.models import ProblemVolume
from django.contrib.auth.models import User

urlpatterns = patterns('',
    (r'^oj/', include('oj.rooturls')),
)

