from django.urls import path
from .views import *


urlpatterns = [
    path('', home_page, name='home'),
    path('subjects/', get_subjects, name='get_subjects'),
    path('subjects/<int:pk>/', get_subject, name='get_subject'),
    path('quizzes/<int:pk>/', get_quiz, name='get_quiz'),
    path('quizzes/<int:quiz_id>/submit/', submit_quiz, name='submit_quiz'),
    path('get-history-quizzes-results/<int:pk>/<str:filter>/', get_history_quizzes_results, name='get_history_quizzes_results')
]
