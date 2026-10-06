import re
from django.db import migrations, models


def populate_townships(apps, schema_editor):
    Station = apps.get_model('DataAccess', 'FireStation')
    for station in Station.objects.using(schema_editor.connection.alias).all():
        # Prefer the address's explicit township over the station's name.
        match = re.search(r'([^၊,\s]+မြို့နယ်)', station.address or '')
        if match is None:
            match = re.search(r'([^၊,\s]+မြို့နယ်)', station.name)
        if match:
            station.township = match.group(1)
            station.save(update_fields=['township'])


class Migration(migrations.Migration):
    dependencies = [('DataAccess', '0009_firereport_closed_at_and_more')]
    operations = [
        migrations.AddField(model_name='firestation', name='township', field=models.CharField('မြို့နယ်', max_length=100, blank=True)),
        migrations.RunPython(populate_townships, migrations.RunPython.noop),
    ]
