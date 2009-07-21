#coding=utf-8
from oj.problem.models import Problem,ProblemImage,ProblemTestData
from django.contrib import admin

class ImageInline(admin.TabularInline):
	model = ProblemImage

class TestDataInline(admin.TabularInline):
	model = ProblemTestData

class ProblemAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields':['title', 'description', 'input', 'output', 'sampleinput', 'sampleoutput']}),
		('Judge Information',{'fields':[ 'origin', 'hint','memorylimit','timelimit',  'judgerule', \
'specialjudge','accept_counts', 'submit_counts'], 'classes': ['collapse'] } ),
	]
	inlines = [ImageInline,TestDataInline]
admin.site.register(Problem,ProblemAdmin)
