from django.db import migrations, models


def populate_identifiers(apps, schema_editor):
    Monitor = apps.get_model('monitor', 'Monitor')
    for m in Monitor.objects.all():
        if not m.identifier:
            # create a stable unique identifier based on PK
            m.identifier = f"mon-{m.pk}"
            m.save()


def reverse_identifiers(apps, schema_editor):
    Monitor = apps.get_model('monitor', 'Monitor')
    for m in Monitor.objects.all():
        m.identifier = None
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0003_remove_monitor_last_seen_remove_monitor_monitor_id_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_identifiers, reverse_identifiers),
        migrations.AlterField(
            model_name='monitor',
            name='identifier',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
