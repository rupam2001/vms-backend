# Generated by Django 5.0.2 on 2024-02-19 06:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_rename_target_user_notification_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user',
            new_name='target_user',
        ),
    ]
