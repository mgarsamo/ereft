# Generated migration for adding guest_house_name field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0011_add_guest_configuration_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='guest_house_name',
            field=models.CharField(blank=True, help_text='Name of the guest house or hotel if this vacation home is part of a larger establishment', max_length=255, null=True),
        ),
    ]
