from django.conf.urls.defaults import *

from django.contrib.auth.models import User


urlpatterns = patterns('',
    (r'^changepassword/$', 'oj.userprofile.views.changepassword'),
    (r'^login/$', 'oj.userprofile.views.login'),
    (r'^logincheck/$', 'oj.userprofile.views.logincheck'),
    (r'^logout/$', 'oj.userprofile.views.logout'),

    (r'^$', 'django.views.generic.list_detail.object_list',
     {'queryset':User.objects.all(), 'paginate_by':20, 'allow_empty':True }),

#    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', {'queryset':User.objects.all()}),


    (r'^(?P<user_id>\d+)/$','oj.userprofile.views.userdetail'),

)
