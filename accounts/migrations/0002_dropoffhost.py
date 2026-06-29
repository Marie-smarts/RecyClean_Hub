# Generated manually for DropOffHost proxy model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DropOffHost',
            fields=[],
            options={
                'verbose_name': 'drop off host',
                'verbose_name_plural': 'drop off hosts',
                'proxy': True,
            },
            bases=('accounts.dropoffcenter',),
        ),
    ]
