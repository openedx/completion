from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import BigAutoField

import model_utils.fields

from completion.models import validate_percent


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockCompletion',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('id', BigAutoField(serialize=False, primary_key=True)),
                ('course_key', CourseKeyField(max_length=255)),
                ('block_key', UsageKeyField(max_length=255)),
                ('block_type', models.CharField(max_length=64)),
                ('completion', models.FloatField(validators=[validate_percent])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='blockcompletion',
            unique_together={('course_key', 'block_key', 'user')},
        ),
        migrations.AlterIndexTogether(
            name='blockcompletion',
            index_together={('course_key', 'block_type', 'user'), ('user', 'course_key', 'modified')},
        ),
    ]
