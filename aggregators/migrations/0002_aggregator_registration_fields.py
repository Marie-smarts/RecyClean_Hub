# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aggregators', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregatorprofile',
            name='national_id_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='aggregatorprofile',
            name='national_id_photo',
            field=models.ImageField(blank=True, null=True, upload_to='aggregator_ids/'),
        ),
        migrations.AddField(
            model_name='aggregatorprofile',
            name='service_area',
            field=models.TextField(blank=True),
        ),
    ]
