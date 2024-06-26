# Generated by Django 5.0.2 on 2024-02-11 16:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_organization_location_organization_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('item_description', models.TextField()),
                ('is_allowed', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='InvitationPass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateTimeField()),
                ('valid_till', models.DateTimeField()),
                ('purpose', models.TextField()),
                ('inv_created_at', models.DateTimeField(auto_now_add=True)),
                ('checked_in_at', models.DateTimeField()),
                ('checked_out_at', models.DateTimeField()),
                ('feedback', models.TextField()),
                ('rating', models.FloatField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_by', to=settings.AUTH_USER_MODEL)),
                ('organization_location', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.location')),
                ('visiting_person', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='visiting_person', to=settings.AUTH_USER_MODEL)),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.visitor')),
            ],
        ),
        migrations.CreateModel(
            name='Belonging',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('identifier_code', models.CharField(max_length=100)),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.invitationpass')),
            ],
        ),
        migrations.CreateModel(
            name='InvitationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_status', models.CharField(max_length=30)),
                ('next_status', models.CharField(max_length=30)),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invitation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.invitationpass')),
            ],
        ),
    ]
