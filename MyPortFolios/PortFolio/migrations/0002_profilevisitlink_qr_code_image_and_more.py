# Generated by Django 5.0 on 2024-03-26 12:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PortFolio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilevisitlink',
            name='qr_code_image',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
        migrations.AlterField(
            model_name='profilevisitlink',
            name='generated_link',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='profilevisitlink',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_visit', to=settings.AUTH_USER_MODEL),
        ),
    ]