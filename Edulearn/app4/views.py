import json
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.urls import reverse
from app.forms import BaseChoiceFormSet, ChoiceForm, QuestionForm, QuizForm
from app.models import Certificate, Choice, Course, Question, Quiz, Student, UserAnswer

# Create your views here.

@login_required
def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="certificate.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)
    certificate, created = Certificate.objects.get_or_create(student=student, course=course)
    
    context = {
        'certificate': certificate,
        'user': request.user,
        'course': course,
    }
    
    template_path = 'certificate.html'
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.title}_certificate.pdf"'
    
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def debug_certificate_view(request, course_id):
    certificate = Certificate.objects.filter(student=request.user.student, course_id=course_id).first()
    
    if not certificate:
        raise Http404("Certificate not found")
    
    context = {'certificate': certificate, 'user': request.user}
    return render(request, 'certificate.html', context)



@login_required
def create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    ChoiceFormSet = formset_factory(ChoiceForm, formset=BaseChoiceFormSet, extra=4)  

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        question_form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)

        if quiz_form.is_valid() and question_form.is_valid() and formset.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.course = course
            quiz.save()

            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            for form in formset:
                if form.cleaned_data:
                    choice = form.save(commit=False)
                    choice.question = question
                    choice.save()

            return redirect('quiz_list', course_id=course.id)
    else:
        quiz_form = QuizForm()
        question_form = QuestionForm()
        formset = ChoiceFormSet()
    for field in quiz_form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
    for field in question_form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
    for form in formset:
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'create_quiz.html', {
        'quiz_form': quiz_form,
        'question_form': question_form,
        'formset': formset,
        'course': course,
    })


@login_required
def quiz_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)
    return render(request, 'quiz_list.html', {'quizzes': quizzes, 'course': course})


@login_required
def quiz_detail(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choice_set')

    if request.method == 'POST':
        user_score = 0
        total_questions = questions.count()

        for question in questions:
            selected_choice_id = request.POST.get(f'question-{question.id}')
            if selected_choice_id:
                selected_choice = Choice.objects.get(id=selected_choice_id)
                UserAnswer.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    selected_choice=selected_choice
                )
                if selected_choice.is_correct:
                    user_score += 1

        return redirect('quiz_results', course_id=course.id, quiz_id=quiz.id)

    return render(request, 'quiz_detail.html', {
        'course': course,
        'quiz': quiz,
        'questions': questions
    })


@login_required
def quiz_results(request, course_id, quiz_id):
    course = get_object_or_404(Course, id=course_id)
    quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choice_set')
    user_answers = UserAnswer.objects.filter(user=request.user, quiz=quiz)
    
    user_score = sum(1 for answer in user_answers if answer.selected_choice.is_correct)
    total_questions = questions.count()

    next_quiz = Quiz.objects.filter(course=course, id__gt=quiz.id).order_by('id').first()
    next_quiz_id = next_quiz.id if next_quiz else None

    return render(request, 'quiz_results.html', {
        'course': course,
        'quiz': quiz,
        'score': user_score,
        'total_questions': total_questions,
        'next_quiz_id': next_quiz_id
    })

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuestionForm()

    return render(request, 'add_question.html', {'form': form, 'quiz': quiz})



@login_required
def submit_quiz_results(request, course_id, quiz_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        quiz = get_object_or_404(Quiz, id=quiz_id, course=course)
        data = json.loads(request.body)
        score = data.get('score', 0)

        
        if 'quiz_scores' not in request.session:
            request.session['quiz_scores'] = {}
        request.session['quiz_scores'][quiz_id] = score
        request.session.modified = True

        
        next_quiz = Quiz.objects.filter(course=course, id__gt=quiz.id).order_by('id').first()
        if next_quiz:
            response = {
                'next_quiz_id': next_quiz.id,
                'next_quiz_url': reverse('quiz_detail', args=[course.id, next_quiz.id]),
            }
        else:
            response = {
                'next_quiz_id': None,
                'course_results_url': reverse('course_results', args=[course.id]),
            }

        return JsonResponse(response)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def course_results(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = Quiz.objects.filter(course=course)
    total_questions = 0
    total_correct = 0

    for quiz in quizzes:
        questions = quiz.question_set.all()
        total_questions += questions.count()

        if 'quiz_scores' in request.session:
            total_correct += request.session['quiz_scores'].get(str(quiz.id), 0)

    return render(request, 'course_results.html', {
        'course': course,
        'total_questions': total_questions,
        'total_correct': total_correct
    })


@login_required
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        user = request.user
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.question_set.all()

        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}_choice')
            selected_choice = get_object_or_404(Choice, id=choice_id)
            UserAnswer.objects.create(user=user, quiz=quiz, question=question, selected_choice=selected_choice)

        return redirect('quiz_results', quiz_id=quiz_id)

    return redirect('quiz_detail', quiz_id=quiz_id)

