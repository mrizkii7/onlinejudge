#coding=utf-8
from django.conf.urls.defaults import *

from oj.problem.models import Problem

urlpatterns = patterns('oj.problem.views',  
#   (r'^/$', 'problemlist'),
	(r'^(?P<problemid>\d+)/$', 'problemdetail'),
	(r'^(?P<problemid>\d+)/submit/$', 'problemsubmit'),
#    (r'^(?P<problemid>\d+)/status/$','problemstatus'),
	(r'^(?P<problemid>\d+)/rejudge/$', 'rejudge_problem'),

)

