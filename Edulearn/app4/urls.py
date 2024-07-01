from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('courses/<int:course_id>/certificate/', views.certificate, name='certificate'),  
    path('courses/<int:course_id>/debug_certificate/', views.debug_certificate_view, name='debug_certificate'),  
    path('create_quiz/<int:course_id>/', views.create_quiz, name='create_quiz'),
    path('courses/<int:course_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/submit/', views.submit_quiz_results, name='submit_quiz_results'),
    path('courses/<int:course_id>/quizzes/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('courses/<int:course_id>/results/', views.course_results, name='course_results'),
    path('quizzes/<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('', include('django.contrib.auth.urls')),
    
]
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)