from django.db import migrations, models


def map_legacy_roles(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for profile in UserProfile.objects.all():
        if profile.role == 'shop_owner':
            profile.role = 'host'
            profile.save(update_fields=['role'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_dropoffhost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='user_type',
            new_name='role',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('household', 'Household'),
                    ('aggregator', 'Aggregator'),
                    ('host', 'Host'),
                    ('recycler', 'Recycler'),
                ],
                default='recycler',
                max_length=20,
            ),
        ),
        migrations.RunPython(map_legacy_roles, migrations.RunPython.noop),
    ]
