import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm, UserRegisterForm, UserEditForm, StaffRegisterForm
from happystudy.forms import *
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import ListView
from .models import CustomUser
from happystudy.models import *
from .utils import custom_login_required, staff_login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Реєстрація успішно завершена.')
            return redirect('signin')
        else:
            messages.error(request, form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/base_form.html', {'form': form, 'title': 'Реєстрація', 'btn_name': 'Відправити'})


def signin(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вхід виконано успішно.')
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/base_form.html', {'form': form, 'title': 'Вхід', 'btn_name': 'Увійти'})


def signout(request):
    logout(request)
    return redirect('home')


@method_decorator(staff_login_required, name='dispatch')
class ListUsers(ListView):
    context_object_name = 'users'
    paginate_by = 10
    model = CustomUser
    template_name = 'accounts/user_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_staff=False)
        return queryset


@staff_login_required
def add_assistant(request):
    if request.method == 'POST':
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.is_superuser = False
            user.save()
            messages.success(request, 'Ви додали помічника!')
            return redirect('user_list')
    else:
        form = StaffRegisterForm()
    return render(request, 'accounts/base_form.html', {'form': form, 'title': 'Реєстрація помічника', 'btn_name': 'Відправити'})


@login_required
def edit_user(request):
    user = get_object_or_404(CustomUser, pk=request.user.pk)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваші дані було успішно оновлено.')
            return redirect('home')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'accounts/base_form.html',
                  {'form': form, 'title': 'Редагування профілю', 'btn_name': 'Зберегти'})


@custom_login_required
def delete_user(request):
    user = get_object_or_404(CustomUser, pk=request.user.pk)

    quizzes = UsersQuizzes.objects.filter(user=user)
    for quiz in quizzes:
        results = Result.objects.filter(user_quiz=quiz)
        for result in results:
            result.delete()
        quiz.delete()

    user.delete()
    return redirect('signout')


@method_decorator(staff_login_required, name='dispatch')
class ListSubjects(ListView):
    context_object_name = 'subjects'
    paginate_by = 15
    model = Subject
    template_name = 'accounts/subject_list.html'

    def get_queryset(self):
        queryset = Subject.objects.order_by('title')
        year = self.request.GET.get('year')
        if year and year != "all":
            year = " ".join(year.split("-"))
            queryset = queryset.filter(school_year=year).order_by('title')
        return queryset

def create_subject(request):
    if request.method == 'POST':
        form = CreateSubjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Предмет додано.')
            return redirect('subject_list')
        else:
            messages.error(request, form.errors)
    else:
        form = CreateSubjectForm()
    return render(request, 'accounts/base_form.html', {'form': form, 'title': 'Створення предмета', 'btn_name': 'Створити'})


@staff_login_required
def edit_subject(request, id):
    subject = get_object_or_404(Subject, id=id)

    if request.method == 'POST':
        form = CreateSubjectForm(request.POST,  request.FILES, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Предмет було успішно оновлено.')
            return redirect('subject_list')
    else:
        form = CreateSubjectForm(instance=subject)
    return render(request, 'accounts/base_form.html',
                  {'form': form, 'title': 'Редагування предмету', 'btn_name': 'Оновити'})


@staff_login_required
def delete_subject(request, id):
    subject = get_object_or_404(Subject, id=id)
    subject.delete()
    messages.success(request, "Предмет успішно видалено.")
    return redirect('subject_list')


@method_decorator(staff_login_required, name='dispatch')
class QuizList(ListView):
    context_object_name = 'quizzes'
    paginate_by = 15
    model = Quiz
    template_name = 'accounts/quiz_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('created_at')
        return queryset


@staff_login_required
def create_quiz(request):
    if request.method == 'GET':
        subjects = Subject.objects.all()
        return render(request, 'accounts/create_quiz.html', {"subjects": subjects})

    elif request.method == 'POST':
        data = json.loads(request.POST['data'])
        files = request.FILES

        if not data['questions']:
            return JsonResponse({'error': 'У теста має бути хоча б одне питання!'}, status=400)

        try:
            subject = get_object_or_404(Subject, pk=data['subject'])
            quiz = Quiz.objects.create(
                title=data['testName'],
                subject=subject
            )

            for i, question_data in enumerate(data['questions']):
                image_key = f'questions[{i}][image]'
                image_file = files.get(image_key)

                question = Question.objects.create(
                    title=question_data['text'],
                    image=image_file,
                    quiz=quiz
                )

                for answer_data in question_data['answers']:
                    Answer.objects.create(
                        question=question,
                        text=answer_data['text'],
                        is_correct=answer_data['is_correct']
                    )

        except IntegrityError:
            return JsonResponse({'error': 'Тест із такою назвою вже існує!'}, status=400)

        except Exception as e:
            return JsonResponse({'error': 'Сталася помилка під час створення тесту!'}, status=500)

        else:
            return JsonResponse({'message': 'Тестування створено!'}, status=201)


@staff_login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    subjects = Subject.objects.all()

    if request.method == 'GET':
        return render(request, 'accounts/edit_quiz.html', {
            'quiz': quiz,
            'subjects': subjects
        })

    elif request.method == 'POST':
        data = json.loads(request.POST['data'])
        files = request.FILES

        if not data['questions']:
            return JsonResponse({'error': 'У теста має бути хоча б одне питання!'}, status=400)

        f_quiz = Quiz.objects.filter(title=data['title']).first()
        if f_quiz and f_quiz.pk != quiz.pk:
            return JsonResponse({'error': 'Тест із такою назвою вже існує!'}, status=400)

        quiz.title = data['title']
        subject = get_object_or_404(Subject, pk=data['subject'])
        quiz.subject = subject
        quiz.save()

        for question_index, question_data in enumerate(data['questions']):
            question_id = question_data['id']
            question = Question.objects.get(pk=question_id)
            question.title = question_data['title']

            image_key = f'questions[{question_index + 1}][image]'
            if image_key in files:
                image_file = files.get(image_key)
                if image_file:
                    question.image = image_file
            elif f'questions[{question_index + 1}][image_removed]' in request.POST:
                question.image = None

            question.save()

            for answer_data in question_data['answers']:
                answer_obj = Answer.objects.get(id=answer_data['id'])
                answer_obj.text = answer_data['text']
                answer_obj.is_correct = answer_data['is_correct']
                answer_obj.save()

        return JsonResponse({'message': 'Тест успішно оновлено!'}, status=201)


@staff_login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete_quiz()
    messages.success(request, "Тест успішно видалено.")
    return redirect('quiz_list')
