# Generated by Django 2.2.13 on 2021-01-22 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20210122_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='gender',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffs',
            name='profile_pic',
            field=models.FileField(default=0, upload_to=''),
            preserve_default=False,
        ),
    ]
