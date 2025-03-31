from django.shortcuts import render
from accounts.models import CustomUser
from .models import *


def home_page(request):
    users= CustomUser.objects.filter(is_staff=False).count()
    quizzes= Quiz.objects.all().count()
    context = {
            'users_count': users,
            'quizzes_count': quizzes
        }
    return render(request, "home.html", context)


def get_subjects(request):
    subjects = Subject.objects.values('title').distinct()

    if request.user.is_authenticated:
        year = request.user.school_year
        if year:
            subjects = Subject.objects.filter(school_year=year).values('title').distinct()

    return render(request, "happystudy/subjects.html", {'subjects': subjects, 'title': 'Предмети'})
