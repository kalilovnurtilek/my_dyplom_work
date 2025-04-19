# Generated by Django 5.1.4 on 2025-04-18 07:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_specialty_alter_post_options_post_application_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='specialties',
        ),
        migrations.AddField(
            model_name='post',
            name='specialty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.specialty', verbose_name='Приоритетная специальность'),
        ),
    ]
