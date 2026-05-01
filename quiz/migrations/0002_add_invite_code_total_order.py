import uuid
import django.db.models.deletion
from django.db import migrations, models


def populate_invite_codes(apps, schema_editor):
    Quiz = apps.get_model('quiz', 'Quiz')
    for quiz in Quiz.objects.filter(invite_code__isnull=True):
        quiz.invite_code = uuid.uuid4().hex[:8].upper()
        quiz.save(update_fields=['invite_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='invite_code',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='participation',
            name='total',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(populate_invite_codes, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['order', 'id']},
        ),
    ]
