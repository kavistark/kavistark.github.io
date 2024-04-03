# Generated by Django 5.0 on 2024-03-26 13:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PortFolio', '0002_profilevisitlink_qr_code_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilevisitlink',
            name='qr_code_image',
        ),
        migrations.AlterField(
            model_name='profilevisitlink',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]