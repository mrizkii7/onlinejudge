from django.conf.urls.defaults import *

from oj.judge.models import Judge


urlpatterns = patterns('oj.judge.views',

	(r'^$', 'judge_list'),

	(r'^(?P<object_id>\d+)/$', 'judge_detail'),

	(r'^(?P<object_id>\d+)/print_ass/$', 'judge_print_ass'),

	(r'^(?P<object_id>\d+)/print_exp/$', 'judge_print_exp'),

	(r'^(?P<object_id>\d+)/rejudge/$', 'judge_rejudge'),

)

