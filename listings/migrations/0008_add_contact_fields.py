# Generated manually to add contact_name and contact_phone fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0007_populate_sample_properties'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='contact_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
