from django.db import models

from django.contrib.auth.models import User
from oj.problem.models import Problem
# Create your models here.

#class UserProfile(models.Model):
#    user = models.OneToOneField(User, edit_inline=False, num_in_admin = 1)
#    submitcounts = models.PositiveIntegerField('Submit Counts', core=True, default = 0)
#    acceptcounts = models.PositiveIntegerField('Accept Counts', core=True, default = 0)
#    acceptproblem = models.ManyToManyField(Problem)
    
#    def __str__(self):
#	return '%s %s' % (self.user.id, self.user.username)

#    class Admin: pass
