from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import CustomUser
from accounts.utils import custom_login_required
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone


def home_page(request):
    users = CustomUser.objects.filter(is_staff=False).count()
    quizzes = Quiz.objects.all().count()
    context = {
            'users_count': users,
            'quizzes_count': quizzes
        }
    return render(request, "home.html", context)


def get_subjects(request):
    subjects = Subject.objects.filter(school_year="5 клас")

    if request.user.is_authenticated:
        year = request.user.school_year
        if year:
            subjects = Subject.objects.filter(school_year=year)

    return render(request, "happystudy/subjects.html", {'subjects': subjects, 'title': 'Предмети'})


def get_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    quizzes = Quiz.objects.filter(subject=subject)

    return render(request, "happystudy/subject.html", {'subject': subject, 'quizzes': quizzes})


@custom_login_required
def get_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    year = request.user.school_year
    if quiz.subject.school_year != year:
        return redirect('get_subject', quiz.subject.pk)

    user_quiz = UsersQuizzes.objects.create(user=request.user, quiz=quiz)
    user_quiz.save()
    return render(request, "happystudy/do_quiz.html", {'quiz': quiz})


@custom_login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user_quiz = UsersQuizzes.objects.filter(user=request.user, quiz=quiz, finished_at__isnull=True).last()

    for question in quiz.questions.all():
        answer_id = request.POST.get(f"question_{question.id}")
        if answer_id:
            answer = Answer.objects.get(pk=answer_id, question=question)
            Result.objects.create(user_quiz=user_quiz, answer=answer)

    user_quiz.finished_at = timezone.now()
    user_quiz.save()

    return redirect('home')


def set_message(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            messages.error(request, message)
        return JsonResponse({'status': 'success'})


@login_required
def get_history_quizzes_results(request, pk, filter):
    user = get_object_or_404(CustomUser, pk=pk)
    if filter == "all":
        user_quizzes = UsersQuizzes.objects.filter(user=user, finished_at__isnull=False).order_by("-finished_at")

    count = user_quizzes.count()
    print(count)
    return render(request, "happystudy/history_data.html", {
        'user_quizzes': user_quizzes, 
        'count': count, 
        'title': 'Історія проходжень',
        'user_pk': pk
    })
