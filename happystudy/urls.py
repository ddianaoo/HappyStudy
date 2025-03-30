from django.urls import path
from .views import *


urlpatterns = [
    path('', home_page, name='home'),
    # path('quizzes/', get_quizzes, name='get_quizzes'),
    # path('choose-category/', choose_quiz_category, name='choose_quiz_category'),
    # path('paper-quizzes/', get_paper_quizzes, name='get_paper_quizzes'),
    # path('category-quizzes/<str:category>/', get_category_quizzes, name='get_category_quizzes'),
    # path('topic-quizzes/', get_topic_quizzes, name='get_topic_quizzes'),
    # path('get-quiz/<int:pk>/', get_quiz, name='get_quiz'),
    # path('get-history-quizzes-results/<int:pk>/<str:filter>/', get_history_quizzes_results, name='get_history_quizzes_results'),
    # path('quiz/<int:quiz_id>/submit_results/', submit_quiz_results, name='submit_quiz_results'),
    # path('set-message/', set_message, name='set_message')
]