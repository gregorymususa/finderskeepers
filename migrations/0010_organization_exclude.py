# Generated by Django 2.1.5 on 2019-05-25 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couponfinder', '0009_organization_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='exclude',
            field=models.BooleanField(default=False, verbose_name='Exclude'),
        ),
    ]