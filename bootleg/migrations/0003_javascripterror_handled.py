# Generated by Django 3.1 on 2020-11-02 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bootleg', '0002_auto_20201102_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='javascripterror',
            name='handled',
            field=models.BooleanField(default=False),
        ),
    ]