# Generated by Django 5.0.2 on 2024-02-16 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_invitationpass_approver_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitationpass',
            name='feedback',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='invitationpass',
            name='rating',
            field=models.FloatField(null=True),
        ),
    ]
