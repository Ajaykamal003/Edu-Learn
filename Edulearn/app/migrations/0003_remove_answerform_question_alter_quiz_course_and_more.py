# Generated by Django 5.0.6 on 2024-06-20 07:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_choiceform_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answerform',
            name='question',
        ),
        migrations.AlterField(
            model_name='quiz',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='app.course'),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='AnswerForm',
        ),
    ]
