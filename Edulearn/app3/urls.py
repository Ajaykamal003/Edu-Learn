from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


urlpatterns = [
    path('login/tutor/', views.login_tutor_view, name='login_tutor'),
    path('tutorcourses/', views.tutorcourse, name='tutorcourse'),
    path('courses/<int:course_id>/tutorcourse_detail', views.tutorcourse_details, name='tutorcourse_details'),
    path('courses/create/', views.create_course, name='createcourse'),
    path('course/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('', include('django.contrib.auth.urls')),

    
]
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)