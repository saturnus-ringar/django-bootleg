# Generated by Django 3.1.4 on 2020-12-13 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bootleg', '0004_auto_20201211_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='loglevel',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Name'),
        ),
    ]
