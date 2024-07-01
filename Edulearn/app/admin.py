from django.contrib import admin
from .models import Course, Tutor, Student, Enrollment, Quiz, Question, Progress, Certificate, Video

# Register your models here.
admin.site.register(Tutor)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Progress)
admin.site.register(Certificate)

class VideoInline(admin.StackedInline):
    model = Video
    extra = 1  # Number of empty forms to display

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [VideoInline]
    exclude = ('videos',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']