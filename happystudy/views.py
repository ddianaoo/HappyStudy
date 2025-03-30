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
