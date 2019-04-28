# Generated by Django 2.1.5 on 2019-04-28 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couponfinder', '0003_auto_20190428_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flag',
            name='flag',
        ),
        migrations.RemoveField(
            model_name='flag',
            name='id',
        ),
        migrations.AddField(
            model_name='flag',
            name='flag_filename',
            field=models.URLField(blank=True, null=True, verbose_name='FlagFilename'),
        ),
        migrations.AlterField(
            model_name='flag',
            name='iso_country_code',
            field=models.SlugField(max_length=2, primary_key=True, serialize=False, verbose_name='IsoCountryCode'),
        ),
    ]
