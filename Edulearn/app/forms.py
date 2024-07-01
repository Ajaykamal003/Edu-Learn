from django import forms
from django.contrib.auth.models import User
from .models import Course, Quiz, Question, Progress  , Choice, Rating , UserAnswer, Video
from django.contrib.auth.forms import UserCreationForm
from django import forms
from app.tasks import send_review_email_task

class TutorRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']   


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'instructor', 'category', 'image']

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'file']

VideoFormSet = forms.inlineformset_factory(
    Course, Video, form=VideoForm,
    extra=1, can_delete=True
)



class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']


class BaseChoiceFormSet(forms.BaseFormSet):
    def clean(self):
        for form in self.forms:
            is_correct = form.cleaned_data.get('is_correct', False)
            if is_correct:
                return
        raise forms.ValidationError('At least one correct choice is required per question')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']


class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['user', 'quiz', 'question', 'selected_choice']


class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['progress']
        

class ReviewForm(forms.Form):
    name = forms.CharField(
        label='Name', min_length=4, max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Full name', 'id': 'form-firstname'}))
    email = forms.EmailField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'E-mail', 'id': 'form-email'}))
    review = forms.CharField(
        label="Review", widget=forms.Textarea (attrs={'class': 'form-control', 'rows': '5'}))
    def send_email(self):
        send_review_email_task.delay(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            review=self.cleaned_data['review']
        )
