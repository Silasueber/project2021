# Generated by Django 3.2.3 on 2021-05-22 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteruser',
            name='userid',
            field=models.CharField(default='', max_length=30),
        ),
    ]