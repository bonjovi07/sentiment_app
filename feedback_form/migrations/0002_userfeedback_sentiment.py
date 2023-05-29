# Generated by Django 4.2.1 on 2023-05-22 20:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feedback_form', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_courtesy', models.IntegerField()),
                ('feedback_quality', models.IntegerField()),
                ('feedback_timeless', models.IntegerField()),
                ('feedback_efficiency', models.IntegerField()),
                ('feedback_cleanliness', models.IntegerField()),
                ('feedback_comfort', models.IntegerField()),
                ('feedback_comments', models.TextField()),
                ('feedback_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedback_form.userclients')),
                ('feedback_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentiment_analysis', models.CharField(max_length=50)),
                ('sentiment_feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feedback_form.userfeedback')),
            ],
        ),
    ]
