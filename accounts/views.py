import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm, UserRegisterForm, UserEditForm
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
from django.forms import formset_factory


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # registration only
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


# @staff_login_required
# def add_assistant(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_staff = True
#             user.is_superuser = False
#             user.save()
#             messages.success(request, 'Ви додали помічника!')
#             return redirect('user_list')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'accounts/signup.html',
#                   {'form': form, 'title': 'Додати помічника'})


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
    paginate_by = 10
    model = Subject
    template_name = 'accounts/subject_list.html'

    def get_queryset(self):
        return Subject.objects.order_by('title') 


def create_subject(request):
    if request.method == 'POST':
        form = CreateSubjectForm(request.POST)
        if form.is_valid():
            # registration only
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
        form = CreateSubjectForm(request.POST, instance=subject)
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


# @method_decorator(staff_login_required, name='dispatch')
# class QuizList(ListView):
#     context_object_name = 'quizzes'
#     paginate_by = 15
#     model = Quiz
#     template_name = 'accounts/quiz_list.html'

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         queryset = queryset.order_by('created_at')
#         return queryset


@staff_login_required
def create_quiz(request):
    if request.method == 'GET':
        subjects = Subject.objects.all()
        return render(request, 'accounts/create_quiz.html', {"subjects": subjects})

    elif request.method == 'POST':
        data = json.loads(request.POST['data'])
        files = request.FILES

        try:
            subject = get_object_or_404(Subject, pk=data['subject'])
            quiz = Quiz.objects.create(
                title=data['testName'],
                subject=subject
            )

            for question_index, question_data in enumerate(data['questions']):
                image_key = f'questions[{question_index}][image]'
                image_file = files.get(image_key) if image_key in files else None

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


# @staff_login_required
# def edit_quiz(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)

#     if request.method == 'GET':
#         questions = [quiz_question.question for quiz_question in quiz.quiz_questions.all()]
#         all_questions = Question.objects.exclude(id__in=[question.id for question in questions])
#         print(questions)
#         return render(request, 'accounts/edit_quiz.html', {
#             'quiz': quiz,
#             'questions': questions,
#             'all_questions': all_questions,
#             'CATEGORY_CHOICES': CATEGORY_CHOICES,
#         })
    
#     elif request.method == 'POST':
#         data = json.loads(request.POST['data'])
#         files = request.FILES
#         quiz.title = data['testName']
#         quiz.category = data['category']
#         quiz.is_random = data['isRandom']
#         quiz.save()

#         quiz.quiz_questions.all().delete()

#         for question_index, question_data in enumerate(data['questions']):
#             question_id = question_data['id']
#             question = Question.objects.get(pk=question_id)
#             question.text = question_data['text']
#             question.explanation = question_data.get('explanation', '')

#             image_key = f'questions[{question_index + 1}][image]'
#             if image_key in files:
#                 image_file = files.get(image_key)
#                 if image_file:
#                     question.image = image_file
#             elif f'questions[{question_index + 1}][image_removed]' in request.POST:
#                 question.image = None

#             question.save()

#             quiz.quiz_questions.create(question=question)

#             for answer_data in question_data['answers']:
#                 answer_obj = Answer.objects.get(id=answer_data['id'])
#                 answer_obj.text = answer_data['text']
#                 answer_obj.is_correct = answer_data['is_correct']
#                 answer_obj.save()

#         return JsonResponse({'message': 'Тест успішно оновлено!'}, status=201)


# @staff_login_required
# def add_question(request):
#     if request.method == 'POST':
#         quiz_ids = request.POST.getlist('quiz_ids')
#         text = request.POST.get('text')
#         explanation = request.POST.get('explanation', '')
#         image = request.FILES.get('image', '')
#         correct_answer = request.POST.get('correct_answer')
#         answers = request.POST.getlist('answers[]')

#         if not quiz_ids or not text or not correct_answer or len(answers) < 2:
#             return JsonResponse({'error': 'Усі поля мають бути заповнені'}, status=400)

#         question = Question.objects.create(text=text, explanation=explanation, image=image)
#         quizzes = Quiz.objects.filter(id__in=quiz_ids)
#         for quiz in quizzes:
#             quiz.quiz_questions.create(question=question)

#         for i, answer_text in enumerate(answers, start=1):
#             Answer.objects.create(
#                 question=question,
#                 text=answer_text,
#                 is_correct=(str(i) == correct_answer)
#             )

#         return JsonResponse({'message': 'Питання додано успішно!'}, status=201)

#     quizzes = Quiz.objects.filter(is_random=False)
#     return render(request, "accounts/add_question.html", {"quizzes": quizzes})


# @staff_login_required
# def edit_question(request, question_id):
#     question = get_object_or_404(Question, id=question_id)
#     if request.method == 'POST':
#         quiz_ids = request.POST.getlist('quiz_ids')
#         text = request.POST.get('text')
#         explanation = request.POST.get('explanation', '')
#         image = request.FILES.get('image', None)
#         correct_answer = request.POST.get('correct_answer')
#         answers = request.POST.getlist('answers[]')

#         if not quiz_ids or not text or not correct_answer or len(answers) < 2:
#             return JsonResponse({'error': 'Усі поля мають бути заповнені'}, status=400)

#         question.text = text
#         question.explanation = explanation
#         question.image = image
#         question.save()

#         question.quiz_questions.all().delete()
#         quizzes = Quiz.objects.filter(id__in=quiz_ids)
#         for quiz in quizzes:
#             quiz.quiz_questions.create(question=question)

#         existing_answers = list(question.answers.all()) 

#         for i, answer_text in enumerate(answers, start=1):
#             if i <= len(existing_answers):
#                 existing_answer = existing_answers[i - 1]
#                 existing_answer.text = answer_text
#                 existing_answer.is_correct = (str(i) == correct_answer)
#                 existing_answer.save()
#         return JsonResponse({'message': 'Питання оновлено успішно!'}, status=200)

#     quizzes = Quiz.objects.all()
#     question_quizzes = question.quiz_questions.values_list('quiz_id', flat=True)
#     return render(request, "accounts/edit_question.html", {
#         "question": question,
#         "quizzes": quizzes,
#         "question_quizzes": question_quizzes,
#     })


# @staff_login_required
# def delete_question(request, question_id):
#     question = get_object_or_404(Question, id=question_id)
#     question.delete_question()
#     return redirect('question_list')
    

# @method_decorator(staff_login_required, name='dispatch')
# class QuestionList(ListView):
#     context_object_name = 'questions'
#     paginate_by = 8
#     model = Question
#     template_name = 'accounts/question_list.html'

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         queryset = queryset.order_by('created_at')
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['quizzes'] = Quiz.objects.all()

#         return context
