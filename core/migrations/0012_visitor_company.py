# Generated by Django 5.0.2 on 2024-02-16 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_notification_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='company',
            field=models.CharField(default='N/A', max_length=255),
        ),
    ]
