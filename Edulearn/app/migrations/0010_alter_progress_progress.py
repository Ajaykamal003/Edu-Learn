# Generated by Django 5.0.6 on 2024-06-29 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='progress',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
