from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ReviewEmailView,alertView

urlpatterns = [
        
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('course/<int:course_id>/content/', views.course_content, name='course_content'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),  
    path('update_progress/<int:course_id>/', views.update_progress, name='update_progress'),
    path('update_video_progress/<int:course_id>/<int:video_id>/', views.update_video_progress, name='update_video_progress'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/progress/', views.update_progress, name='update_progress'),
    path('messenger/',ReviewEmailView.as_view(),name='messenger'),
    path('alert/',alertView,name='alert'),
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)