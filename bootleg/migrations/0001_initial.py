# Generated by Django 3.1.2 on 2020-10-29 02:06

import django.db.models.manager
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='JavascriptErrorMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=8192)),
            ],
            options={
                'verbose_name': 'Javascript-error-message',
                'verbose_name_plural': 'Javascript-error-messages',
            },
        ),
        migrations.CreateModel(
            name='LogLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LoggedException',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('stack_trace', models.TextField(null=True)),
                ('args', models.CharField(max_length=1024)),
                ('handled', models.BooleanField(default=False)),
                ('clazz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bootleg.class')),
            ],
            options={
                'verbose_name': 'Logged exception',
                'verbose_name_plural': 'Logged exceptions',
            },
            managers=[
                ('unhandled', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='JavascriptError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('ip', models.GenericIPAddressField()),
                ('url', models.URLField()),
                ('line', models.IntegerField()),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bootleg.javascripterrormessage')),
            ],
            options={
                'verbose_name': 'Javascript-error',
                'verbose_name_plural': 'Javascript-errors',
            },
        ),
        migrations.CreateModel(
            name='DjangoLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('stack_trace', models.TextField(null=True)),
                ('args', models.CharField(max_length=1024)),
                ('handled', models.BooleanField(default=False)),
                ('filename', models.CharField(max_length=1024)),
                ('clazz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bootleg.class')),
                ('log_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bootleg.loglevel')),
            ],
            options={
                'verbose_name': 'Django-log-entry',
                'verbose_name_plural': 'Django-log-entries',
            },
            managers=[
                ('unhandled', django.db.models.manager.Manager()),
            ],
        ),
    ]
