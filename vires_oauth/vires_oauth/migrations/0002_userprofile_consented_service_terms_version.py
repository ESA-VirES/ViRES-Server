# Generated by Django 2.2.2 on 2019-10-28 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vires_oauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='consented_service_terms_version',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
    ]
