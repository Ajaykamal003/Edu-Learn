from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('subject/', views.subject, name='subject'),
    path('team/', views.team, name='team'),
    path('about/', views.about, name='about'),
    path('404error/', views.error , name='error'),
    path('service/', views.service, name='service'), 
    path('profile/', views.profile, name='profile'), 
    path('courses/', views.course_list, name='course_list'),
   
]
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)