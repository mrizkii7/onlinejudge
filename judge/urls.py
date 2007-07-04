from django.conf.urls.defaults import *

from oj.judge.models import Judge


urlpatterns = patterns('',

    (r'^$', 'oj.judge.views.judge_filter'),

    (r'^(?P<object_id>\d+)/$', 'oj.judge.views.judge_detail'),

    (r'^(?P<object_id>\d+)/print_ass/$', 'oj.judge.views.judge_print_ass'),

    (r'^(?P<object_id>\d+)/print_exp/$', 'oj.judge.views.judge_print_exp'),

    (r'^(?P<object_id>\d+)/rejudge/$', 'oj.judge.views.judge_rejudge'),

)

