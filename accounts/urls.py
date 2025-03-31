from django.urls import path
from .views import *


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('edit-account/', edit_user, name='edit_user'),
    path('delete-account/', delete_user, name='delete_user'),
    path('users/', ListUsers.as_view(), name='user_list'),
    # path('add-assistant/', add_assistant, name='add_assistant'),


    # path('questions/', QuestionList.as_view(), name='question_list'),
    # path('create-question/', add_question, name='create_question'),
    # path('edit-question/<int:question_id>/', edit_question, name='edit_question'),
    # path('delete-question/<int:question_id>/', delete_question, name='delete_question'),

    # path('quizzes/', QuizList.as_view(), name='quiz_list'),
    # path('create-quiz/', create_quiz, name='create_quiz'),
    # path('edit-quiz/<int:quiz_id>/', edit_quiz, name='edit_quiz'),
    # path('delete-quiz/<int:quiz_id>/', delete_quiz, name='delete_quiz'),


    path('subjects/', ListSubjects.as_view(), name='subject_list'),
    path('create-subject/', create_subject, name='create_subject'),
    path('edit-subject/<int:id>/', edit_subject, name='edit_subject'),
    path('delete-subject/<int:id>/', delete_subject, name='delete_subject'),
]
