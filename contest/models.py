#coding=utf-8
from django.db import models

# Create your models here.

from oj.problem.models import Problem
from django.contrib.auth.models import Group


class Contest(models.Model):
	title = models.CharField('标题', max_length = 256)
	description = models.TextField('描述', blank=True)
	problem = models.ManyToManyField(Problem, blank = True, verbose_name = u"问题")
	permittedgroups = models.ManyToManyField(Group, blank = True, verbose_name = u"有权限的组")
	start_time = models.DateTimeField('开始时间')
	end_time = models.DateTimeField('结束时间')
	is_public = models.BooleanField('公开')
	
	def __unicode__(self):
		return u'%d %s' % (self.id,self.title)
	class Admin: 
		pass
	class Meta:
		verbose_name = verbose_name_plural = u'比赛'

