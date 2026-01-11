# Generated migration to add guest configuration fields for vacation homes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0010_add_vacation_home_fields_and_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='max_adults',
            field=models.PositiveIntegerField(default=2, help_text='Maximum number of adults allowed'),
        ),
        migrations.AddField(
            model_name='property',
            name='max_children',
            field=models.PositiveIntegerField(default=0, help_text='Maximum number of children allowed (ages 0-17)'),
        ),
        migrations.AddField(
            model_name='property',
            name='pets_allowed',
            field=models.BooleanField(default=False, help_text='Whether pets are allowed on the property'),
        ),
    ]
