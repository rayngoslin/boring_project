from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/join/', views.join_quiz, name='join_quiz'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quizzes/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quizzes/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('quizzes/<int:quiz_id>/questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]
