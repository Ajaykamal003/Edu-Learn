from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from app.forms import CourseForm, VideoFormSet
from app.models import Course, Enrollment, Progress, Quiz, Student, Video

# Create your views here.

def login_tutor_view(request):
    error_message = ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tutorcourse')
            else:
                error_message = 'Invalid username or password.'
        else:
            error_message = 'Invalid form data.'
    else:
        form = AuthenticationForm()
    return render(request, 'login_tutor.html', {'form': form, 'error_message': error_message})



@login_required
def tutorcourse(request):
    courses = Course.objects.all()
    for course in courses:
        course.image_url = course.image.url if course.image else None
    return render(request, 'tutorcourse_list.html', {'courses': courses})



@login_required
def tutorcourse_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    videos = course.videos.all()
    student, created = Student.objects.get_or_create(user=request.user)
    quizzes = Quiz.objects.filter(course=course)
    first_quiz = quizzes.first()  
    enrolled = Enrollment.objects.filter(course=course, student=student).exists()
    progress = None
    if enrolled:
        progress, created = Progress.objects.get_or_create(student=request.user.student, course=course)
    
    return render(request, 'tutorcourse_detail.html', {
        'course': course, 
        'videos': videos,
        'quizzes': quizzes, 
        'first_quiz': first_quiz,  
        'enrolled': enrolled, 
        'progress': progress
    })



@login_required
def create_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if course_form.is_valid() and formset.is_valid():
            course = course_form.save(commit=False)
            course.instructor = request.user.tutor  
            course.save()
            videos = formset.save(commit=False)
            for video in videos:
                video.course = course
                video.save()
            formset.save_m2m()
            return redirect('tutorcourse')  

    else:
        course_form = CourseForm()
        formset = VideoFormSet(queryset=Video.objects.none())

    context = {
        'course_form': course_form,
        'formset': formset,
        'existing_courses': Course.objects.filter(instructor=request.user.tutor),
    }
    return render(request, 'create_course.html', context)


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES, instance=course)
        formset = VideoFormSet(request.POST, request.FILES, instance=course)

        if course_form.is_valid() and formset.is_valid():
            course = course_form.save()
            formset.save()
            return redirect('tutorcourse')  

    else:
        course_form = CourseForm(instance=course)
        formset = VideoFormSet(instance=course)

    has_image = bool(course.image)

    context = {
        'course_form': course_form,
        'formset': formset,
        'has_image': has_image,
    }
    return render(request, 'edit_course.html', context)

