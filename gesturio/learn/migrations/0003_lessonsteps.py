# Generated by Django 5.1.7 on 2025-05-12 10:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0002_category_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonSteps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.IntegerField()),
                ('sign_name', models.TextField()),
                ('image', models.URLField(blank=True, null=True)),
                ('video', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='learn.lesson')),
            ],
            options={
                'ordering': ['step_number'],
            },
        ),
    ]
