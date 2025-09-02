# Generated migration for Ethiopia address fields and square meter units

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        # Add Ethiopia-specific address fields
        migrations.AddField(
            model_name='property',
            name='sub_city',
            field=models.CharField(max_length=100, blank=True, null=True, help_text='Sub-city (e.g., Bole, Kirkos)'),
        ),
        migrations.AddField(
            model_name='property',
            name='kebele',
            field=models.CharField(max_length=100, blank=True, null=True, help_text='Kebele/Ward'),
        ),
        migrations.AddField(
            model_name='property',
            name='street_name',
            field=models.CharField(max_length=255, blank=True, null=True, help_text='Street name'),
        ),
        migrations.AddField(
            model_name='property',
            name='house_number',
            field=models.CharField(max_length=50, blank=True, null=True, help_text='House/building number'),
        ),
        
        # Add square meter field
        migrations.AddField(
            model_name='property',
            name='area_sqm',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='Area in square meters'),
        ),
        migrations.AddField(
            model_name='property',
            name='lot_size_sqm',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='Lot size in square meters'),
        ),
        migrations.AddField(
            model_name='property',
            name='price_per_sqm',
            field=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Price per square meter'),
        ),
        
        # Set default status for new listings
        migrations.AddField(
            model_name='property',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('active', 'Active'),
                    ('pending', 'Pending Review'),
                    ('inactive', 'Inactive'),
                    ('sold', 'Sold'),
                    ('rented', 'Rented'),
                ],
                default='active',
                help_text='Property listing status'
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Whether the listing is published and visible'),
        ),
    ]
