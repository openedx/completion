# Dont create User foreign key constraint in db to avoid locking up the user table during course completion updates.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('completion', '0003_learning_context'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockcompletion',
            name='user',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
