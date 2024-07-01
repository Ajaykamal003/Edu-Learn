import os
from django.contrib.auth import logout
from django.core.files import File
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Rating,  Student, Course, Enrollment, Progress, Certificate, Video, VideoProgress 
from .forms import  RatingForm, UserRegistrationForm,   ReviewForm 
from django.http import  JsonResponse
from .utils import generate_certificate
from app.forms import ReviewForm
from django.views.generic.edit import FormView
from django.shortcuts import render,redirect

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    error_message = ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'tutor'):
                    return redirect('tutorcourse')
                else:
                    return redirect('course_list')
            else:
                error_message = 'Invalid username or password.'
        else:
            error_message = 'Invalid form data.'
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'error_message': error_message})



def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    videos = course.videos.all()
    quizzes = course.quizzes.all()
    first_quiz = quizzes.first()
    ratings = Rating.objects.filter(course=course)
   
    enrolled = False
   
    if request.user.is_authenticated:
        student, created = Student.objects.get_or_create(user=request.user)
        enrolled = Enrollment.objects.filter(course=course, student=student).exists()
   
    if request.method == 'POST' and enrolled:
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.course = course
            rating.student = student
            rating.save()
            return redirect('course_detail', course_id=course.id)
    else:
        rating_form = RatingForm()
    
    context = {
        'course': course,
        'videos': videos,
        'quizzes': quizzes,
        'first_quiz': first_quiz,
        'enrolled': enrolled,
        'ratings': ratings,
        'rating_form': rating_form,
    }
    return render(request, 'course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student, created = Student.objects.get_or_create(user=request.user)
    enrollment, created = Enrollment.objects.get_or_create(course=course, student=student)
    return redirect('course_content', course_id=course.id)

@login_required
def course_content(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    videos = course.videos.all()
    quizzes = course.quizzes.all()
    first_quiz = quizzes.first() if quizzes else None

    student = get_object_or_404(Student, user=request.user)
    enrollment = get_object_or_404(Enrollment, course=course, student=student)
    progress, created = Progress.objects.get_or_create(student=student, course=course)

   
    total_items = videos.count() + quizzes.count()
    if total_items > 0:
        completed_items = 0
        for video in videos:
            if video.completed:  
                completed_items += 1
        for quiz in quizzes:
            if quiz.completed:  
                completed_items += 1

        progress.progress = (completed_items / total_items) * 100
        progress.save()

    context = {
        'course': course,
        'videos': videos,
        'quizzes': quizzes,
        'first_quiz': first_quiz,
        'progress': progress,
    }
    return render(request, 'course_content.html', context)

@login_required
@require_POST
def update_video_progress(request, course_id, video_id):
    course = get_object_or_404(Course, id=course_id)
    video = get_object_or_404(Video, id=video_id, course=course)
    student = get_object_or_404(Student, user=request.user)
    
    progress = float(request.POST.get('progress', 0))
    
    video_progress, created = VideoProgress.objects.get_or_create(
        student=student,
        video=video,
        defaults={'progress': progress}
    )
    
    if not created:
        video_progress.progress = progress
        video_progress.save()
    
    if progress >= 100:
        video_progress.completed = True
        video_progress.save()
    
    course_progress = calculate_course_progress(student, course)
    
    return JsonResponse({'success': True, 'progress': course_progress})


@login_required
def calculate_course_progress(student, course):
    videos = course.videos.all()
    total_videos = videos.count()
    completed_videos = VideoProgress.objects.filter(
        student=student,
        video__course=course,
        completed=True
    ).count()
    
    progress = (completed_videos / total_videos) * 100 if total_videos > 0 else 0
    
    course_progress, created = Progress.objects.get_or_create(
        student=student,
        course=course,
        defaults={'progress': progress}
    )
    
    if not created:
        course_progress.progress = progress
        course_progress.save()
    
    return progress


@login_required
@require_POST
def update_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)
    
    videos = course.videos.all()
    total_videos = videos.count()
    completed_videos = videos.filter(completed=True).count()
    
    progress, created = Progress.objects.get_or_create(student=student, course=course)
    progress.progress = (completed_videos / total_videos) * 100
    progress.save()
    
    response_data = {'success': True, 'progress': progress.progress}
    
    if progress.progress == 100:
        certificate, created = Certificate.objects.get_or_create(student=student, course=course)
        if created:
            file_path = generate_certificate(student, course)
            with open(file_path, 'rb') as f:
                certificate.certificate_file.save(os.path.basename(file_path), File(f))
            response_data['certificate_url'] = certificate.certificate_file.url

    return JsonResponse(response_data)


class ReviewEmailView(FormView):
    template_name = 'message.html'
    form_class = ReviewForm

    def form_valid(self, form):
        form.send_email()
        return redirect('alert')
   
def alertView(request):
    msg = "Thanks For Your Review"
    return render(request,'alerts.html',{'msg':msg})

