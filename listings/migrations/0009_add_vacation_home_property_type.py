# Generated migration to add vacation_home property type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0008_add_contact_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(choices=[('house', 'House'), ('apartment', 'Apartment'), ('condo', 'Condo'), ('townhouse', 'Townhouse'), ('vacation_home', 'Vacation Home'), ('land', 'Land'), ('commercial', 'Commercial'), ('other', 'Other')], max_length=20),
        ),
    ]
