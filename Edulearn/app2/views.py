from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from app.models import Course
# Create your views here.

def home(request):
    context = {}
    return render(request, 'index.html', context)

def onlinedg(request):
    return render(request, 'onlinedegree.html')

def shortc(request):
    return render(request, 'shortcourse.html')

def webe(request):
    return render(request, 'webexpert.html')

def subject(request):
    context = {}
    return render(request,'subjects.html', context)

def team(request):
    context = {}
    return render(request,'team.html', context)

def about(request):
    context = {}
    return render(request, 'about.html', context)

def error(request):
    context = {}
    return render(request, '404.html',context)

def service(request):
    context = {}
    return render(request, 'service.html', context)


@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})
