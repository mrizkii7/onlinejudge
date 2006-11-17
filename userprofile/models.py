#coding=utf-8
from django.db import models

from django.contrib.auth.models import User
from oj.problem.models import Problem
from oj.judge.models import Judge
# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True,verbose_name = '用户')
    submit_counts = models.PositiveIntegerField('提交总数', default = 0)
    accept_counts = models.PositiveIntegerField('正确提交数', default = 0)
    accept_problems = models.ManyToManyField(Problem, blank = True)
    accept_problems_counts = models.PositiveIntegerField('正确题数', default = 0)

    def __str__(self):
        return '%d %s %s' % (self.user.id, self.user.username, self.user.first_name)

    class Admin:
        list_display = ('user', 'accept_problems_counts', 'accept_counts', 'submit_counts')

    class Meta:
        ordering = ['-accept_problems_counts', 'submit_counts']
        verbose_name = verbose_name_plural = '用户数据'

