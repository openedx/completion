# -*- coding: utf-8 -*-
# Changes completion to track blocks for any learning context,
# and not just for courses.
#
# This migration does not produce any database-level changes. You can verify
# this with: ./manage.py lms sqlmigrate completion 0003

from django.conf import settings
from django.db import migrations
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('completion', '0002_auto_20180125_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockcompletion',
            name='course_key',
            field=opaque_keys.edx.django.models.LearningContextKeyField(db_column='course_key', max_length=255),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='blockcompletion',
            old_name='course_key',
            new_name='context_key',
        ),
        migrations.AlterUniqueTogether(
            name='blockcompletion',
            unique_together=set([('context_key', 'block_key', 'user')]),
        ),
        migrations.AlterIndexTogether(
            name='blockcompletion',
            index_together=set([('user', 'context_key', 'modified'), ('context_key', 'block_type', 'user')]),
        ),
    ]
